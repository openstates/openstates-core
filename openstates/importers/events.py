from .base import BaseImporter
from ._types import _JsonDict
from ..utils import get_pseudo_id, _make_pseudo_id
from ..data.models import (
    Event,
    EventLocation,
    EventSource,
    EventDocument,
    EventDocumentLink,
    EventLink,
    EventParticipant,
    EventMedia,
    EventMediaLink,
    EventAgendaItem,
    EventRelatedEntity,
    EventAgendaMedia,
    EventAgendaMediaLink,
)
from .organizations import OrganizationImporter
from .vote_events import VoteEventImporter
from .bills import BillImporter


class EventImporter(BaseImporter):
    _type = "event"
    model_class = Event
    related_models = {
        "sources": (EventSource, "event_id", {}),
        "documents": (
            EventDocument,
            "event_id",
            {"links": (EventDocumentLink, "document_id", {})},
        ),
        "links": (EventLink, "event_id", {}),
        "participants": (EventParticipant, "event_id", {}),
        "media": (EventMedia, "event_id", {"links": (EventMediaLink, "media_id", {})}),
        "agenda": (
            EventAgendaItem,
            "event_id",
            {
                "related_entities": (EventRelatedEntity, "agenda_item_id", {}),
                "media": (
                    EventAgendaMedia,
                    "agenda_item_id",
                    {"links": (EventAgendaMediaLink, "media_id", {})},
                ),
            },
        ),
    }
    preserve_order = {"agenda"}

    def __init__(
        self,
        jurisdiction_id: str,
        org_importer: OrganizationImporter,
        bill_importer: BillImporter,
        vote_event_importer: VoteEventImporter,
    ):
        super(EventImporter, self).__init__(jurisdiction_id)
        self.org_importer = org_importer
        self.bill_importer = bill_importer
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
        # TODO: geocode here?
        return obj

    def prepare_for_db(self, data: _JsonDict) -> _JsonDict:
        data["jurisdiction_id"] = self.jurisdiction_id
        data["location"] = self.get_location(data["location"])

        data["start_date"] = data["start_date"]
        data["end_date"] = data.get("end_date", "")

        for participant in data["participants"]:
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
                    # unpack and repack bill psuedo id in case filters alter it
                    bill = get_pseudo_id(entity["bill_id"])
                    self.bill_importer.apply_transformers(bill)
                    bill = _make_pseudo_id(**bill)
                    entity["bill_id"] = self.bill_importer.resolve_json_id(
                        bill, allow_no_match=True
                    )
                elif "vote_event_id" in entity:
                    entity["vote_event_id"] = self.vote_event_importer.resolve_json_id(
                        entity["vote_event_id"], allow_no_match=True
                    )

        return data
