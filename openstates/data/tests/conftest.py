import pytest
from datetime import datetime
from openstates.data.models import (
    Jurisdiction,
    Division,
    Membership,
    Organization,
    Person,
    Post,
    LegislativeSession,
    Event,
    EventLocation,
    VoteEvent,
    Bill,
)


@pytest.fixture
def division():
    div = Division.objects.create(
        id="ocd-division/country:us/state:mo", name="Missouri"
    )
    return div


@pytest.fixture
def jurisdiction(division):
    juris = Jurisdiction.objects.create(
        id="ocd-jurisdiction/country:us/state:mo/government",
        name="Missouri State Senate",
        url="http://www.senate.mo.gov",
        division=division,
    )
    return juris


@pytest.fixture
def legislative_session(jurisdiction):
    l_s = LegislativeSession.objects.create(
        jurisdiction=jurisdiction,
        identifier=2017,
        name="2017 Session",
        start_date="2017-01-04",
        end_date="2017-05-25",
    )
    return l_s


@pytest.fixture
def organization():
    org = Organization.objects.create(name="Missouri State Senate")
    return org


@pytest.fixture
def bill(legislative_session):
    b = Bill.objects.create(
        legislative_session=legislative_session,
        identifier="HR 3590",
        title="The Patient Protection and Affordable Care Act",
    )
    return b


@pytest.fixture
def vote_event(legislative_session, organization):
    v_e = VoteEvent.objects.create(
        motion_text="That the House do now proceed to the Orders of the Day.",
        start_date="2017-02-16",
        result="pass",
        organization=organization,
        legislative_session=legislative_session,
    )
    return v_e


@pytest.fixture
def event_location(jurisdiction):
    loc = EventLocation.objects.create(
        name="State Legislative Building", jurisdiction=jurisdiction,
    )
    return loc


@pytest.fixture
def event(jurisdiction, event_location):
    e = Event.objects.create(
        name="Meeting of the Committee on Energy",
        jurisdiction=jurisdiction,
        description="To discuss the pros/cons of wind farming.",
        classification="committee-meeting",
        start_date=datetime.utcnow().isoformat().split(".")[0],
        status="passed",
        location=event_location,
    )
    return e


@pytest.fixture
def party():
    p = Organization.objects.create(name="Republican", classification="party")
    return p


@pytest.fixture
def person():
    p = Person.objects.create(name="Arnold Schwarzenegger")
    return p


@pytest.fixture
def senator(jurisdiction, party):
    div_id = "ocd-division/country:us/state:mo/sldu:1"
    person = Person.objects.create(
        name="Willy Worm", current_role={"org_classification": "upper", "district": 1}
    )
    senate = Organization.objects.create(
        classification="upper", name="Senate", jurisdiction=jurisdiction
    )
    division = Division.objects.create(id=div_id, name="MO 1")
    post = Post.objects.create(
        organization=senate, division=division, role="Senator", label="1"
    )
    person.memberships.create(organization=senate, post=post)
    person.memberships.create(organization=party)
    return person


@pytest.fixture
def post(organization):
    p = Post.objects.create(organization=organization, label="Governor")
    return p


@pytest.fixture
def membership(organization, post, person):
    m = Membership.objects.create(organization=organization, post=post, person=person)
    return m
