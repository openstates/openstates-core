from datetime import date, timedelta
from ..exceptions import ScrapeValueError
from ..utils import _make_pseudo_id
from .base import BaseModel, SourceMixin, AssociatedLinkMixin, LinkMixin
from .schemas.event import schema


def calculate_window(*, base_day=None, days_before=30, days_after=90):
    """ given details on a window, returns start & end dates for windowing purposes """
    if not base_day:
        base_day = date.today()
    start = base_day - timedelta(days=days_before)
    end = base_day + timedelta(days=days_after)
    return start, end


class EventAgendaItem(dict, AssociatedLinkMixin):
    event = None

    def __init__(self, description, event):
        super(EventAgendaItem, self).__init__(
            {
                "description": description,
                "classification": [],
                "related_entities": [],
                "subjects": [],
                "media": [],
                "notes": [],
                "order": len(event.agenda),
                "extras": {},
            }
        )
        self.event = event

    def add_subject(self, what):
        self["subjects"].append(what)

    def add_classification(self, what):
        self["classification"].append(what)

    def add_vote_event(self, vote_event, *, id=None, note="consideration"):
        self.add_entity(name=vote_event, entity_type="vote_event", id=id, note=note)

    def add_committee(self, committee, *, id=None, note="participant"):
        self.add_entity(name=committee, entity_type="organization", id=id, note=note)

    def add_bill(self, bill, *, id=None, note="consideration"):
        self.add_entity(name=bill, entity_type="bill", id=id, note=note)

    def add_person(self, person, *, id=None, note="participant"):
        self.add_entity(name=person, entity_type="person", id=id, note=note)

    def add_media_link(
        self,
        note,
        url,
        media_type,
        *,
        on_duplicate="warn",
        date="",
        classification="",
    ):
        return self._add_associated_link(
            collection="media",
            note=note,
            url=url,
            media_type=media_type,
            on_duplicate=on_duplicate,
            date=date,
            classification=classification,
        )

    def add_entity(self, name, entity_type, *, id, note):
        ret = {"name": name, "entity_type": entity_type, "note": note}
        if id:
            ret["id"] = id
        elif entity_type:
            if entity_type in ("organization", "person"):
                id = _make_pseudo_id(name=name)
            elif entity_type in ("bill", "vote_event"):
                id = _make_pseudo_id(identifier=name)
            else:
                raise ScrapeValueError(
                    "attempt to call add_entity with unsupported "
                    "entity type: {}".format(entity_type)
                )
            ret[entity_type + "_id"] = id

        self["related_entities"].append(ret)


class Event(BaseModel, SourceMixin, AssociatedLinkMixin, LinkMixin):
    """
    Details for an event in .format
    """

    _type = "event"
    _schema = schema

    def __init__(
        self,
        name,
        start_date,
        location_name,
        *,
        all_day=False,
        description="",
        end_date="",
        status="confirmed",
        classification="event",
        upstream_id="",
    ):
        super(Event, self).__init__()
        self.start_date = start_date
        self.all_day = all_day
        self.end_date = end_date
        self.name = name
        self.description = description
        self.status = status
        self.classification = classification
        self.upstream_id = upstream_id
        self.location = {"name": location_name, "note": "", "coordinates": None}
        self.documents = []
        self.participants = []
        self.media = []
        self.agenda = []

    def __str__(self):
        return "{} {}".format(self.start_date, self.name.strip())

    def set_location(self, name, *, note="", url="", coordinates=None):
        self.location = {
            "name": name,
            "note": note,
            "url": url,
            "coordinates": coordinates,
        }

    def add_participant(self, name, type, *, id=None, note="participant"):
        p = {"name": name, "entity_type": type, "note": note}
        if id:
            p["id"] = id
        elif type:
            id = _make_pseudo_id(name=name)
            p[type + "_id"] = id

        self.participants.append(p)

    def add_person(self, name, *, id=None, note="participant"):
        return self.add_participant(name=name, type="person", id=id, note=note)

    def add_committee(self, name, *, id=None, note="participant"):
        return self.add_participant(name=name, type="organization", id=id, note=note)

    def add_agenda_item(self, description):
        obj = EventAgendaItem(description, self)
        self.agenda.append(obj)
        return obj

    def add_bill(self, bill, *, note="consideration", agenda_item="Associated Bills"):
        """
        adds a dummy agenda item for associating bills for cases where we want bills
        but don't have appropriate agenda items

        context: https://github.com/openstates/enhancement-proposals/pull/28#issuecomment-898720989
        """
        for item in self.agenda:
            if item["description"] == agenda_item:
                break
        else:
            item = EventAgendaItem(agenda_item, self)
            self.agenda.append(item)
        item.add_bill(bill, note=note)

    def add_media_link(
        self,
        note,
        url,
        media_type,
        *,
        on_duplicate="error",
        date="",
        classification="",
    ):
        return self._add_associated_link(
            collection="media",
            note=note,
            url=url,
            media_type=media_type,
            on_duplicate=on_duplicate,
            date=date,
            classification=classification,
        )

    def add_document(
        self,
        note,
        url,
        *,
        media_type="",
        on_duplicate="error",
        date="",
        classification="",
    ):
        return self._add_associated_link(
            collection="documents",
            note=note,
            url=url,
            media_type=media_type,
            on_duplicate=on_duplicate,
            date=date,
            classification=classification,
        )
