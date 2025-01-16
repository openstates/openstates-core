import pytest
from openstates.scrape import Event as ScrapeEvent
from openstates.importers import (
    EventImporter,
    BillImporter,
    VoteEventImporter,
)
from openstates.data.models import (
    Person,
    Membership,
    Organization,
    Jurisdiction,
    Division,
    VoteEvent,
    Bill,
    Event,
)

jid = "ocd-jurisdiction/country:us/state:ne/government"
ojid = "ocd-jurisdiction/country:us/state:ca/government"


def create_jurisdiction():
    Division.objects.create(id="ocd-division/country:us", name="USA")
    j = Jurisdiction.objects.create(id=jid, division_id="ocd-division/country:us")
    return j


def create_other_jurisdiction():
    Division.objects.create(id="ocd-division/country:ca", name="USA")
    j = Jurisdiction.objects.create(id=ojid, division_id="ocd-division/country:ca")
    return j


def ge():
    event = ScrapeEvent(
        name="America's Birthday",
        start_date="2014-07-04T05:00:00+00:00",
        location_name="America",
        all_day=True,
    )
    return event


bi = BillImporter(jid)
vei = VoteEventImporter(jid, bi)


@pytest.mark.django_db
def test_related_people_event():
    create_jurisdiction()
    george = Person.objects.create(id="gw", name="George Washington")
    john = Person.objects.create(id="jqp", name="John Q. Public")
    o = Organization.objects.create(
        name="Merica", jurisdiction_id=jid, classification="legislature"
    )

    Membership.objects.create(person=george, organization=o)
    Membership.objects.create(person=john, organization=o)

    event1 = ge()
    event2 = ge()

    for event in [event1, event2]:
        item = event.add_agenda_item("Cookies will be served")
        item.add_person(person="John Q. Public")
        event.add_person("George Washington")

    result = EventImporter(jid, vei).import_data([event1.as_dict()])
    assert result["event"]["insert"] == 1

    result = EventImporter(jid, vei).import_data([event2.as_dict()])
    assert result["event"]["noop"] == 1

    assert (
        Event.objects.get(name="America's Birthday").participants.first().person_id
        == "gw"
    )

    assert (
        Event.objects.get(name="America's Birthday")
        .agenda.first()
        .related_entities.first()
        .person_id
        == "jqp"
    )


@pytest.mark.django_db
def test_related_vote_event():
    j = create_jurisdiction()
    session = j.legislative_sessions.create(name="1900", identifier="1900")
    org = Organization.objects.create(id="org-id", name="House", classification="lower")
    bill = Bill.objects.create(
        id="bill-1", identifier="HB 1", legislative_session=session
    )
    VoteEvent.objects.create(
        id="vote-1",
        identifier="Roll no. 12",
        bill=bill,
        legislative_session=session,
        organization=org,
    )

    event1 = ge()
    event2 = ge()

    for event in [event1, event2]:
        item = event.add_agenda_item("Cookies will be served")
        item.add_vote_event(vote_event="Roll no. 12")

    result = EventImporter(jid, vei).import_data([event1.as_dict()])
    assert result["event"]["insert"] == 1

    result = EventImporter(jid, vei).import_data([event2.as_dict()])
    assert result["event"]["noop"] == 1

    assert (
        Event.objects.get(name="America's Birthday")
        .agenda.first()
        .related_entities.first()
        .vote_event_id
        == "vote-1"
    )


@pytest.mark.django_db
def test_related_bill_event():
    j = create_jurisdiction()
    session = j.legislative_sessions.create(
        name="2014", identifier="2014", start_date="2014-01-01", end_date="2015-01-01"
    )
    Organization.objects.create(id="org-id", name="House", classification="lower")
    Bill.objects.create(id="bill-1", identifier="HB 101", legislative_session=session)
    event1 = ge()
    event2 = ge()

    for event in [event1, event2]:
        item = event.add_agenda_item("Cookies will be served")
        item.add_bill(bill="HB 101")

    result = EventImporter(jid, vei).import_data([event1.as_dict()])
    assert result["event"]["insert"] == 1

    result = EventImporter(jid, vei).import_data([event2.as_dict()])
    assert result["event"]["noop"] == 1

    assert (
        Event.objects.get(name="America's Birthday")
        .agenda.first()
        .related_entities.first()
        .bill_id
        == "bill-1"
    )


@pytest.mark.django_db
def test_related_bill_event_duplicate_id_use_session():
    # need a fresh BillImporter here to avoid caching from other tests
    j = create_jurisdiction()
    session = j.legislative_sessions.create(
        name="2010", identifier="2010", start_date="2010-01-01", end_date="2010-01-01"
    )
    session2 = j.legislative_sessions.create(
        name="2014", identifier="2014", start_date="2014-01-01", end_date="2015-01-01"
    )
    Organization.objects.create(id="org-id", name="House", classification="lower")
    Bill.objects.create(id="bill-1", identifier="HB 101", legislative_session=session)
    Bill.objects.create(id="bill-2", identifier="HB 101", legislative_session=session2)
    event = ge()
    item = event.add_agenda_item("Cookies will be served")
    item.add_bill(bill="HB 101")

    result = EventImporter(jid, vei).import_data([event.as_dict()])
    assert result["event"]["insert"] == 1

    assert (
        Event.objects.get(name="America's Birthday")
        .agenda.first()
        .related_entities.first()
        .bill_id
        == "bill-2"
    )


@pytest.mark.django_db
def test_related_committee_event():
    j = create_jurisdiction()
    j.legislative_sessions.create(name="1900", identifier="1900")
    org = Organization.objects.create(
        id="org-id", name="House", classification="lower", jurisdiction=j
    )
    Organization.objects.create(
        id="fiscal",
        name="Fiscal Committee",
        classification="committee",
        parent=org,
        jurisdiction=j,
    )

    event1 = ge()
    event2 = ge()

    for event in [event1, event2]:
        item = event.add_agenda_item("Cookies will be served")
        item.add_committee(committee="Fiscal Committee")

    result = EventImporter(jid, vei).import_data([event1.as_dict()])
    assert result["event"]["insert"] == 1

    result = EventImporter(jid, vei).import_data([event2.as_dict()])
    assert result["event"]["noop"] == 1

    assert (
        Event.objects.get(name="America's Birthday")
        .agenda.first()
        .related_entities.first()
        .organization_id
        == "fiscal"
    )


@pytest.mark.django_db
def test_media_event():
    create_jurisdiction()
    event1 = ge()
    event2 = ge()

    for event in [event1, event2]:
        item = event.add_agenda_item("Cookies will be served")
        item.add_media_link(
            note="Hello, World",
            media_type="application/octet-stream",
            url="http://hello.world/foo",
        )

    result = EventImporter(jid, vei).import_data([event1.as_dict()])
    assert result["event"]["insert"] == 1

    result = EventImporter(jid, vei).import_data([event2.as_dict()])
    assert result["event"]["noop"] == 1


@pytest.mark.django_db
def test_media_document():
    create_jurisdiction()
    event1 = ge()
    event2 = ge()

    for event in [event1, event2]:
        event.add_document(
            note="Presentation", url="http://example.com/presentation.pdf"
        )

    result = EventImporter(jid, vei).import_data([event1.as_dict()])
    assert result["event"]["insert"] == 1

    result = EventImporter(jid, vei).import_data([event2.as_dict()])
    assert result["event"]["noop"] == 1


@pytest.mark.django_db
def test_full_event():
    create_jurisdiction()
    george = Person.objects.create(id="gw", name="George Washington")
    o = Organization.objects.create(name="Merica", jurisdiction_id=jid)
    Membership.objects.create(person=george, organization=o)

    event = ge()

    result = EventImporter(jid, vei).import_data([event.as_dict()])
    assert result["event"]["insert"] == 1

    event = ge()

    result = EventImporter(jid, vei).import_data([event.as_dict()])
    assert result["event"]["noop"] == 1

    event = ge()
    event.location["name"] = "United States of America"
    result = EventImporter(jid, vei).import_data([event.as_dict()])
    assert result["event"]["update"] == 1


@pytest.mark.django_db
def test_dedupe_key_event():
    create_jurisdiction()
    create_other_jurisdiction()
    george = Person.objects.create(id="gw", name="George Washington")
    o = Organization.objects.create(name="Merica", jurisdiction_id=jid)
    Membership.objects.create(person=george, organization=o)

    event = ge()
    event.dedupe_key = "foo"

    result = EventImporter(jid, vei).import_data([event.as_dict()])
    assert result["event"]["insert"] == 1

    result = EventImporter(jid, vei).import_data([event.as_dict()])
    assert result["event"]["noop"] == 1

    event.name = ("America's Anniversary",)
    event.location["name"] = "United States of America"
    result = EventImporter(jid, vei).import_data([event.as_dict()])
    assert result["event"]["update"] == 1

    event.dedupe_key = "bar"
    result = EventImporter(jid, vei).import_data([event.as_dict()])
    assert result["event"]["insert"] == 1

    result = EventImporter(ojid, vei).import_data([event.as_dict()])
    assert result["event"]["insert"] == 1


# @pytest.mark.django_db
# def test_bad_event_date():
#     create_jurisdiction()
#     event = ge()
#     event.start_date = '2017'
#     pytest.raises(
#         ValueError,
#         EventImporter('jid', vei).import_item,
#         event.as_dict()
#     )


@pytest.mark.django_db
def test_top_level_media_event():
    create_jurisdiction()
    event1, event2 = ge(), ge()

    event1.add_media_link(
        "fireworks",
        "http://example.com/fireworks.mov",
        media_type="application/octet-stream",
    )
    event2.add_media_link(
        "fireworks",
        "http://example.com/fireworks.mov",
        media_type="application/octet-stream",
    )

    result = EventImporter(jid, vei).import_data([event1.as_dict()])
    assert result["event"]["insert"] == 1

    result = EventImporter(jid, vei).import_data([event2.as_dict()])
    assert result["event"]["noop"] == 1


@pytest.mark.django_db
def test_event_agenda_item():
    create_jurisdiction()
    event1 = ge()

    agenda = event1.add_agenda_item("first item")
    agenda["extras"] = {"one": 1, "two": [2]}

    result = EventImporter(jid, vei).import_data([event1.as_dict()])
    assert result["event"]["insert"] == 1

    e = Event.objects.get()
    a = e.agenda.all()[0]
    assert a.extras == {"one": 1, "two": [2]}


@pytest.mark.django_db
def test_event_soft_deletion():
    create_jurisdiction()
    event1 = ge()
    event2 = ge()
    event2.name = "Other Event"
    result = EventImporter(jid, vei).import_data([event1.as_dict(), event2.as_dict()])
    assert result["event"]["insert"] == 2
    assert Event.objects.count() == 2

    # delete
    result = EventImporter(jid, vei).import_data([event1.as_dict()])
    assert result["event"]["noop"] == 1
    # TODO: assert result["event"]["deleted"] == 1
    assert Event.objects.count() == 2
    assert Event.objects.get(deleted=True).name == "Other Event"

    # undelete
    result = EventImporter(jid, vei).import_data([event1.as_dict(), event2.as_dict()])
    assert result["event"]["update"] == 1
    assert result["event"]["noop"] == 1
    assert Event.objects.count() == 2
    assert Event.objects.filter(deleted=True).count() == 0
