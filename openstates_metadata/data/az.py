from ..models import State, Chamber, simple_numbered_districts

AZ = State(
    name="Arizona",
    abbr="AZ",
    capital="Phoenix",
    capital_tz="America/Denver",
    fips="04",
    unicameral=False,
    legislature_name="Arizona State Legislature",
    division_id="ocd-division/country:us/state:az",
    jurisdiction_id="ocd-jurisdiction/country:us/state:az/government",
    url="http://www.azleg.gov/",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=60,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:az", "lower", 30, num_seats=2
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=30,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:az", "upper", 30
        ),
    ),
)
