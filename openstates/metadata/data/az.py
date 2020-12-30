from ..models import State, Chamber, simple_numbered_districts

AZ = State(
    name="Arizona",
    abbr="AZ",
    capital="Phoenix",
    capital_tz="America/Phoenix",
    fips="04",
    unicameral=False,
    legislature_name="Arizona State Legislature",
    legislature_organization_id="ocd-organization/920fc27e-e574-4700-8ada-221fdf683268",
    executive_name="Office of the Governor",
    executive_organization_id="ocd-organization/69fd6d9c-6730-42a7-ae22-31a4a111603c",
    division_id="ocd-division/country:us/state:az",
    jurisdiction_id="ocd-jurisdiction/country:us/state:az/government",
    url="http://www.azleg.gov/",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        organization_id="ocd-organization/b00585a8-0bd5-4a6b-bde1-1c96400f882f",
        num_seats=60,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:az", "lower", 30, num_seats=2
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        organization_id="ocd-organization/c3d4c85b-888e-4188-b903-a251b957c162",
        num_seats=30,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:az", "upper", 30
        ),
    ),
)
