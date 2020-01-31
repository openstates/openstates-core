from ..models import State, Chamber, simple_numbered_districts

AR = State(
    name="Arkansas",
    abbr="AR",
    capital="Little Rock",
    capital_tz="America/Chicago",
    fips="05",
    unicameral=False,
    legislature_name="Arkansas General Assembly",
    division_id="ocd-division/country:us/state:ar",
    jurisdiction_id="ocd-jurisdiction/country:us/state:ar/government",
    url="http://www.arkleg.state.ar.us",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        organization_id="ocd-organization/9e2c94af-8e67-438b-8a47-7eac48112403",
        num_seats=100,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:ar", "lower", 100
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        organization_id="ocd-organization/f80b9e71-0c25-4b8b-a87d-7266a3f84313",
        num_seats=35,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:ar", "upper", 35
        ),
    ),
)
