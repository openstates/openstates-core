from .base import BaseImporter
from ._types import _JsonDict
from ..utils import get_pseudo_id
from ..data.models import (
    Event,
    EventLocation,
    EventDocument,
    EventParticipant,
    EventMedia,
    EventAgendaItem,
    EventRelatedEntity,
    EventAgendaMedia,
)
from .organizations import OrganizationImporter
from .vote_events import VoteEventImporter


class EventImporter(BaseImporter):
    _type = "event"
    model_class = Event
    related_models = {
        "documents": (
            EventDocument,
            "event_id",
            {},
        ),
        "participants": (EventParticipant, "event_id", {}),
        "media": (EventMedia, "event_id", {}),
        "agenda": (
            EventAgendaItem,
            "event_id",
            {
                "related_entities": (EventRelatedEntity, "agenda_item_id", {}),
                "media": (EventAgendaMedia, "agenda_item_id", {}),
            },
        ),
    }
    preserve_order = {"agenda"}

    def __init__(
        self,
        jurisdiction_id: str,
        vote_event_importer: VoteEventImporter,
    ):
        super(EventImporter, self).__init__(jurisdiction_id)
        self.org_importer = OrganizationImporter(jurisdiction_id)
        self.vote_event_importer = vote_event_importer

    def get_object(self, event: _JsonDict) -> Event:
        if event.get("dedupe_key"):
            spec = {
                "dedupe_key": event.get("dedupe_key"),
                "jurisdiction_id": self.jurisdiction_id,
            }
        else:
            spec = {
                "name": event["name"],
                "description": event["description"],
                "start_date": event["start_date"],
                "end_date": event["end_date"],
                "jurisdiction_id": self.jurisdiction_id,
            }
        return self.model_class.objects.get(**spec)

    def get_location(self, location_data: _JsonDict) -> EventLocation:
        obj, created = EventLocation.objects.get_or_create(
            name=location_data["name"],
            url=location_data.get("url", ""),
            jurisdiction_id=self.jurisdiction_id,
        )
        return obj

    def prepare_for_db(self, data: _JsonDict) -> _JsonDict:
        data["jurisdiction_id"] = self.jurisdiction_id
        data["location"] = self.get_location(data["location"])

        # all objects being inserted should be non-deleted
        data["deleted"] = False
        data["start_date"] = data["start_date"]
        data["end_date"] = data.get("end_date", "")

        for participant in data["participants"]:
            # conversion from old/incorrect names first
            if "committee_id" in participant:
                participant["organization_id"] = participant.pop("committee_id")
            if "legislator_id" in participant:
                participant["person_id"] = participant.pop("legislator_id")

            if "person_id" in participant:
                participant["person_id"] = self.resolve_person(participant["person_id"])
            elif "organization_id" in participant:
                participant["organization_id"] = self.org_importer.resolve_json_id(
                    participant["organization_id"], allow_no_match=True
                )

        for item in data["agenda"]:
            for entity in item["related_entities"]:
                if "person_id" in entity:
                    entity["person_id"] = self.resolve_person(entity["person_id"])
                elif "organization_id" in entity:
                    entity["organization_id"] = self.org_importer.resolve_json_id(
                        entity["organization_id"], allow_no_match=True
                    )
                elif "bill_id" in entity:
                    bill = get_pseudo_id(entity["bill_id"])
                    entity["bill_id"] = self.resolve_bill(
                        bill["identifier"], date=data["start_date"]
                    )
                elif "vote_event_id" in entity:
                    entity["vote_event_id"] = self.vote_event_importer.resolve_json_id(
                        entity["vote_event_id"], allow_no_match=True
                    )

        return data

    def postimport(self) -> None:
        all_db_ids = self.json_to_db_id.values()
        update_set = Event.objects.filter(
            jurisdiction_id=self.jurisdiction_id, deleted=False
        ).exclude(id__in=all_db_ids)
        update_set.update(deleted=True)
