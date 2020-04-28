import re
import pytest
from openstates.scrape import VoteEvent as ScrapeVoteEvent, Bill as ScrapeBill
from openstates.importers import VoteEventImporter, BillImporter
from openstates.data.models import (
    Jurisdiction,
    Person,
    Organization,
    Division,
    VoteEvent,
    LegislativeSession,
    Bill,
)


class DumbMockImporter(object):
    """ this is a mock importer that implements a resolve_json_id that is just a pass-through """

    def resolve_json_id(self, json_id, allow_no_match=False):
        return json_id


def create_jurisdiction():
    Division.objects.create(id="ocd-division/country:us", name="USA")
    j = Jurisdiction.objects.create(id="jid", division_id="ocd-division/country:us")
    j.legislative_sessions.create(name="1900", identifier="1900")
    Organization.objects.create(name="House", classification="lower", jurisdiction=j)
    Organization.objects.create(name="Senate", classification="upper", jurisdiction=j)
    return j


@pytest.mark.django_db
def test_full_vote_event():
    create_jurisdiction()
    bill = ScrapeBill("HB 1", "1900", "Axe & Tack Tax Act", chamber="lower")
    vote_event = ScrapeVoteEvent(
        legislative_session="1900",
        motion_text="passage",
        start_date="1900-04-01",
        classification="passage:bill",
        result="pass",
        bill_chamber="lower",
        bill="HB 1",
        chamber="lower",
    )
    vote_event.set_count("yes", 20)
    vote_event.yes("John Smith")
    vote_event.no("Adam Smith")

    Person.objects.create(name="John Smith")
    Person.objects.create(name="Adam Smith")
    for person in Person.objects.all():
        person.memberships.create(
            organization=Organization.objects.get(classification="lower")
        )

    bi = BillImporter("jid")
    bi.import_data([bill.as_dict()])

    VoteEventImporter("jid", bi).import_data([vote_event.as_dict()])

    assert VoteEvent.objects.count() == 1
    ve = VoteEvent.objects.get()
    assert ve.legislative_session == LegislativeSession.objects.get()
    assert ve.motion_classification == ["passage:bill"]
    assert ve.bill == Bill.objects.get()
    count = ve.counts.get()
    assert count.option == "yes"
    assert count.value == 20
    votes = list(ve.votes.all())
    assert len(votes) == 2
    for v in ve.votes.all():
        if v.voter_name == "John Smith":
            assert v.option == "yes"
            assert v.voter == Person.objects.get(name="John Smith")
        else:
            assert v.option == "no"
            assert v.voter == Person.objects.get(name="Adam Smith")


@pytest.mark.django_db
def test_vote_event_identifier_dedupe():
    j = create_jurisdiction()
    Organization.objects.create(
        id="org-id", name="Legislature", classification="legislature", jurisdiction=j
    )

    vote_event = ScrapeVoteEvent(
        legislative_session="1900",
        start_date="2013",
        classification="anything",
        result="passed",
        motion_text="a vote on something",
        identifier="Roll Call No. 1",
    )
    bi = BillImporter("jid")

    _, what = VoteEventImporter("jid", bi).import_item(vote_event.as_dict())
    assert what == "insert"
    assert VoteEvent.objects.count() == 1

    # same exact vote event, no changes
    _, what = VoteEventImporter("jid", bi).import_item(vote_event.as_dict())
    assert what == "noop"
    assert VoteEvent.objects.count() == 1

    # new info, update
    vote_event.result = "failed"
    _, what = VoteEventImporter("jid", bi).import_item(vote_event.as_dict())
    assert what == "update"
    assert VoteEvent.objects.count() == 1

    # new bill, insert
    vote_event.identifier = "Roll Call 2"
    _, what = VoteEventImporter("jid", bi).import_item(vote_event.as_dict())
    assert what == "insert"
    assert VoteEvent.objects.count() == 2


@pytest.mark.django_db
def test_vote_event_pupa_identifier_dedupe():
    j = create_jurisdiction()
    Organization.objects.create(
        id="org-id", name="Legislature", classification="legislature", jurisdiction=j
    )

    vote_event = ScrapeVoteEvent(
        legislative_session="1900",
        start_date="2013",
        classification="anything",
        result="passed",
        motion_text="a vote on something",
        identifier="Roll Call No. 1",
    )
    vote_event.pupa_id = "foo"

    bi = BillImporter("jid")
    _, what = VoteEventImporter("jid", bi).import_item(vote_event.as_dict())
    assert what == "insert"
    assert VoteEvent.objects.count() == 1

    # same exact vote event, no changes
    _, what = VoteEventImporter("jid", bi).import_item(vote_event.as_dict())
    assert what == "noop"
    assert VoteEvent.objects.count() == 1

    # new info, update
    vote_event.result = "failed"
    _, what = VoteEventImporter("jid", bi).import_item(vote_event.as_dict())
    assert what == "update"
    assert VoteEvent.objects.count() == 1

    # new bill identifier, update
    vote_event.identifier = "First Roll Call"
    _, what = VoteEventImporter("jid", bi).import_item(vote_event.as_dict())
    assert what == "update"
    assert VoteEvent.objects.count() == 1

    # new identifier, insert
    vote_event.pupa_id = "bar"
    _, what = VoteEventImporter("jid", bi).import_item(vote_event.as_dict())
    assert what == "insert"
    assert VoteEvent.objects.count() == 2


@pytest.mark.django_db
def test_vote_event_bill_id_dedupe():
    create_jurisdiction()
    bill = Bill.objects.create(
        id="bill-1",
        identifier="HB 1",
        legislative_session=LegislativeSession.objects.get(),
        from_organization=Organization.objects.get(classification="lower"),
    )
    bill2 = Bill.objects.create(
        id="bill-2",
        identifier="HB 2",
        legislative_session=LegislativeSession.objects.get(),
        from_organization=Organization.objects.get(classification="lower"),
    )

    vote_event = ScrapeVoteEvent(
        legislative_session="1900",
        start_date="2013",
        classification="anything",
        result="passed",
        motion_text="a vote on something",
        bill=bill.identifier,
        bill_chamber="lower",
        chamber="lower",
    )
    bi = BillImporter("jid")

    _, what = VoteEventImporter("jid", bi).import_item(vote_event.as_dict())
    assert what == "insert"
    assert VoteEvent.objects.count() == 1

    # same exact vote event, no changes
    _, what = VoteEventImporter("jid", bi).import_item(vote_event.as_dict())
    assert what == "noop"
    assert VoteEvent.objects.count() == 1

    # new info, update
    vote_event.result = "failed"
    _, what = VoteEventImporter("jid", bi).import_item(vote_event.as_dict())
    assert what == "update"
    assert VoteEvent.objects.count() == 1

    # new vote event, insert
    vote_event = ScrapeVoteEvent(
        legislative_session="1900",
        start_date="2013",
        classification="anything",
        result="passed",
        motion_text="a vote on something",
        bill=bill2.identifier,
        bill_chamber="lower",
        chamber="lower",
    )
    _, what = VoteEventImporter("jid", bi).import_item(vote_event.as_dict())
    assert what == "insert"
    assert VoteEvent.objects.count() == 2


@pytest.mark.django_db
def test_vote_event_bill_clearing():
    # ensure that we don't wind up with vote events sitting around forever on bills as
    # changes make it look like there are multiple vote events
    create_jurisdiction()
    bill = Bill.objects.create(
        id="bill-1",
        identifier="HB 1",
        legislative_session=LegislativeSession.objects.get(),
        from_organization=Organization.objects.get(classification="lower"),
    )
    Bill.objects.create(
        id="bill-2",
        identifier="HB 2",
        legislative_session=LegislativeSession.objects.get(),
        from_organization=Organization.objects.get(classification="lower"),
    )
    bi = BillImporter("jid")

    vote_event1 = ScrapeVoteEvent(
        legislative_session="1900",
        start_date="2013",
        classification="anything",
        result="passed",
        motion_text="a vote on somthing",  # typo intentional
        bill=bill.identifier,
        bill_chamber="lower",
        chamber="lower",
    )
    vote_event2 = ScrapeVoteEvent(
        legislative_session="1900",
        start_date="2013",
        classification="anything",
        result="passed",
        motion_text="a vote on something else",
        bill=bill.identifier,
        bill_chamber="lower",
        chamber="lower",
    )

    # have to use import_data so postimport is called
    VoteEventImporter("jid", bi).import_data(
        [vote_event1.as_dict(), vote_event2.as_dict()]
    )
    assert VoteEvent.objects.count() == 2

    # a typo is fixed, we don't want 3 vote events now
    vote_event1.motion_text = "a vote on something"
    VoteEventImporter("jid", bi).import_data(
        [vote_event1.as_dict(), vote_event2.as_dict()]
    )
    assert VoteEvent.objects.count() == 2


@pytest.mark.django_db
def test_vote_event_bill_actions():
    create_jurisdiction()
    bill = ScrapeBill("HB 1", "1900", "Axe & Tack Tax Act", chamber="lower")

    # add actions, passage of upper & lower on same day, something else,
    # then passage in upper again on a different day
    bill.add_action(description="passage", date="1900-04-01", chamber="upper")
    bill.add_action(description="passage", date="1900-04-01", chamber="lower")
    bill.add_action(description="other event", date="1900-04-01", chamber="lower")
    bill.add_action(description="passage", date="1900-04-02", chamber="upper")

    # four passage votes, one per chamber, one on 04-01, and one on 04-02
    ve1 = ScrapeVoteEvent(
        legislative_session="1900",
        motion_text="passage",
        start_date="1900-04-01",
        classification="passage:bill",
        result="pass",
        bill_chamber="lower",
        bill="HB 1",
        bill_action="passage",
        chamber="lower",
    )
    ve2 = ScrapeVoteEvent(
        legislative_session="1900",
        motion_text="passage",
        start_date="1900-04-01",
        classification="passage:bill",
        result="pass",
        bill_chamber="lower",
        bill="HB 1",
        bill_action="passage",
        chamber="upper",
    )
    ve3 = ScrapeVoteEvent(
        legislative_session="1900",
        motion_text="passage",
        start_date="1900-04-02",
        classification="passage:bill",
        result="pass",
        bill_chamber="lower",
        bill="HB 1",
        bill_action="passage",
        chamber="lower",
    )
    ve4 = ScrapeVoteEvent(
        legislative_session="1900",
        motion_text="passage",
        start_date="1900-04-02",
        classification="passage:bill",
        result="pass",
        bill_chamber="lower",
        bill="HB 1",
        bill_action="passage",
        chamber="upper",
    )

    bi = BillImporter("jid")
    bi.import_data([bill.as_dict()])

    VoteEventImporter("jid", bi).import_data(
        [ve1.as_dict(), ve2.as_dict(), ve3.as_dict(), ve4.as_dict()]
    )

    bill = Bill.objects.get()
    votes = list(VoteEvent.objects.all())
    actions = list(bill.actions.all())
    assert len(actions) == 4
    assert len(votes) == 4

    votes = {
        (v.organization.classification, v.start_date): v.bill_action for v in votes
    }

    # ensure that votes are matched using action, chamber, and date
    assert votes[("upper", "1900-04-01")] == actions[0]
    assert votes[("lower", "1900-04-01")] == actions[1]
    assert votes[("upper", "1900-04-02")] == actions[3]
    assert votes[("lower", "1900-04-02")] is None


@pytest.mark.django_db
def test_vote_event_bill_actions_two_stage():
    # this test is very similar to what we're testing in test_vote_event_bill_actions w/
    # ve3 and ve4, that two bills that reference the same action won't conflict w/ the
    # OneToOneField, but in this case we do it in two stages so that the conflict is found
    # even if the votes weren't in the same scrape
    create_jurisdiction()
    bill = ScrapeBill("HB 1", "1900", "Axe & Tack Tax Act", chamber="lower")

    bill.add_action(description="passage", date="1900-04-02", chamber="lower")

    ve1 = ScrapeVoteEvent(
        legislative_session="1900",
        motion_text="passage",
        start_date="1900-04-02",
        classification="passage:bill",
        result="pass",
        bill_chamber="lower",
        bill="HB 1",
        bill_action="passage",
        chamber="lower",
    )
    ve2 = ScrapeVoteEvent(
        legislative_session="1900",
        motion_text="passage",
        start_date="1900-04-02",
        classification="passage:bill",
        result="pass",
        bill_chamber="lower",
        bill="HB 1",
        bill_action="passage",
        chamber="lower",
    )
    # disambiguate them
    ve1.pupa_id = "one"
    ve2.pupa_id = "two"

    bi = BillImporter("jid")
    bi.import_data([bill.as_dict()])

    # first imports just fine
    VoteEventImporter("jid", bi).import_data([ve1.as_dict()])
    votes = list(VoteEvent.objects.all())
    assert len(votes) == 1
    assert votes[0].bill_action is not None

    # when second is imported, ensure that action stays pinned to first just as it would
    # have if they were both in same import
    VoteEventImporter("jid", bi).import_data([ve1.as_dict(), ve2.as_dict()])
    votes = list(VoteEvent.objects.all())
    assert len(votes) == 2
    assert votes[0].bill_action is not None
    assert votes[1].bill_action is None


@pytest.mark.django_db
def test_vote_event_bill_actions_errors():
    create_jurisdiction()
    bill = ScrapeBill("HB 1", "1900", "Axe & Tack Tax Act", chamber="lower")

    # for this bill, two identical actions, so vote matching will fail
    bill.add_action(description="passage", date="1900-04-01", chamber="lower")
    bill.add_action(description="passage", date="1900-04-01", chamber="lower")
    # this action is good, but two votes will try to match it
    bill.add_action(description="passage", date="1900-04-02", chamber="lower")

    # will match two actions
    ve1 = ScrapeVoteEvent(
        legislative_session="1900",
        motion_text="passage",
        start_date="1900-04-01",
        classification="passage:bill",
        result="pass",
        bill_chamber="lower",
        bill="HB 1",
        identifier="1",
        bill_action="passage",
        chamber="lower",
    )
    # will match no actions
    ve2 = ScrapeVoteEvent(
        legislative_session="1900",
        motion_text="passage",
        start_date="1900-04-01",
        classification="passage:bill",
        result="pass",
        bill_chamber="lower",
        bill="HB 1",
        identifier="2",
        bill_action="committee result",
        chamber="lower",
    )
    # these two votes will both match the same action
    ve3 = ScrapeVoteEvent(
        legislative_session="1900",
        motion_text="passage",
        start_date="1900-04-02",
        classification="passage:bill",
        result="pass",
        bill_chamber="lower",
        bill="HB 1",
        identifier="3",
        bill_action="passage",
        chamber="lower",
    )
    ve4 = ScrapeVoteEvent(
        legislative_session="1900",
        motion_text="passage-syz",
        start_date="1900-04-02",
        classification="passage:bill",
        result="fail",
        bill_chamber="lower",
        bill="HB 1",
        identifier="4",
        bill_action="passage",
        chamber="lower",
    )

    bi = BillImporter("jid")
    bi.import_data([bill.as_dict()])

    VoteEventImporter("jid", bi).import_data(
        [ve1.as_dict(), ve2.as_dict(), ve3.as_dict(), ve4.as_dict()]
    )

    bill = Bill.objects.get()
    votes = list(VoteEvent.objects.all().order_by("identifier"))

    # isn't matched, was ambiguous across two actions
    assert votes[0].bill_action is None
    # isn't matched, no match in actions
    assert votes[1].bill_action is None

    # these both try to match the same action, only first will succeed
    assert votes[2].bill_action is not None
    assert votes[3].bill_action is None


@pytest.mark.django_db
def test_fix_bill_id():
    create_jurisdiction()
    bill = ScrapeBill(
        "HB 1", "1900", "Test Bill ID", classification="bill", chamber="lower"
    )

    from openstates.settings import IMPORT_TRANSFORMERS

    IMPORT_TRANSFORMERS["bill"] = {
        "identifier": lambda x: re.sub(r"([A-Z]*)\s*0*([-\d]+)", r"\1 \2", x, 1)
    }

    bi = BillImporter("jid")
    bi.import_data([bill.as_dict()])

    ve = ScrapeVoteEvent(
        legislative_session="1900",
        motion_text="passage",
        start_date="1900-04-02",
        classification="passage:bill",
        result="fail",
        bill_chamber="lower",
        bill="HB1",
        identifier="4",
        bill_action="passage",
        chamber="lower",
    )

    VoteEventImporter("jid", bi).import_data([ve.as_dict()])

    IMPORT_TRANSFORMERS["bill"] = {}

    ve = VoteEvent.objects.get()
    ve.bill.identifier == "HB 1"
