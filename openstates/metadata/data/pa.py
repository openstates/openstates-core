from ..models import State, Chamber, simple_numbered_districts

PA = State(
    name="Pennsylvania",
    abbr="PA",
    capital="Harrisburg",
    capital_tz="America/New_York",
    fips="42",
    unicameral=False,
    legislature_name="Pennsylvania General Assembly",
    legislature_organization_id="ocd-organization/4a283791-567b-48b8-aac3-c94c36e3e63a",
    executive_name="Office of the Governor",
    executive_organization_id="ocd-organization/ea33e6ed-4944-5e83-888b-c98b070907ce",
    division_id="ocd-division/country:us/state:pa",
    jurisdiction_id="ocd-jurisdiction/country:us/state:pa/government",
    url="http://www.legis.state.pa.us/",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        organization_id="ocd-organization/0f78429d-ec86-4333-9338-17708fe11914",
        num_seats=203,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:pa", "lower", 203
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        organization_id="ocd-organization/9443a886-8032-4502-b99d-551735ec9606",
        num_seats=50,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:pa", "upper", 50
        ),
    ),
)
