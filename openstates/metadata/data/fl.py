from ..models import State, Chamber, simple_numbered_districts

FL = State(
    name="Florida",
    abbr="FL",
    capital="Tallahassee",
    capital_tz="America/New_York",
    fips="12",
    unicameral=False,
    legislature_name="Florida Legislature",
    legislature_organization_id="ocd-organization/a0b3ad5f-c852-483b-b746-444d3d795701",
    executive_name="Office of the Governor",
    executive_organization_id="ocd-organization/392f8763-ef77-5ce1-9b8e-643b129c3bd3",
    division_id="ocd-division/country:us/state:fl",
    jurisdiction_id="ocd-jurisdiction/country:us/state:fl/government",
    url="http://myflorida.com",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        organization_id="ocd-organization/8b0147dc-8942-4fd5-91c4-a72a92a8e1fe",
        num_seats=120,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:fl", "lower", 120
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        organization_id="ocd-organization/c540c1bb-d614-4174-86db-a146526169f8",
        num_seats=40,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:fl", "upper", 40
        ),
    ),
)
