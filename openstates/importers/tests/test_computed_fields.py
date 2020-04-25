import pytest
from openstates.data.models import Jurisdiction, Division, Organization, Bill
from ..computed_fields import update_bill_fields


def create_data():
    Division.objects.create(id="ocd-division/country:us", name="USA")
    j = Jurisdiction.objects.create(id="jid", division_id="ocd-division/country:us")
    org = Organization.objects.create(
        jurisdiction=j, name="House", classification="lower"
    )
    j.legislative_sessions.create(identifier="1899", name="1899")
    session = j.legislative_sessions.create(identifier="1900", name="1900").id

    return session, org


@pytest.mark.django_db
def test_update_bill_basic():
    session, org = create_data()
    b = Bill.objects.create(
        identifier="HB1", title="One", legislative_session_id=session
    )
    # order doesn't matter compared to date
    b.actions.create(
        date="2020-04-20", description="Introduced", order=100, organization=org
    )
    b.actions.create(
        date="2020-04-21",
        description="Passed House",
        order=2,
        organization=org,
        classification=["passage"],
    )
    # two actions on final date, order=4 should win as latest action description
    b.actions.create(
        date="2020-04-22", description="Something Else", order=3, organization=org
    )
    b.actions.create(
        date="2020-04-22", description="Amended in Senate", order=4, organization=org
    )

    update_bill_fields(b)
    assert b.first_action_date == "2020-04-20"
    assert b.latest_action_date == "2020-04-22"
    assert b.latest_passage_date == "2020-04-21"
    assert b.latest_action_description == "Amended in Senate"
