from ..models import State, Chamber, simple_numbered_districts

MT = State(
    name="Montana",
    abbr="MT",
    capital="Helena",
    capital_tz="America/Denver",
    fips="30",
    unicameral=False,
    legislature_name="Montana Legislature",
    division_id="ocd-division/country:us/state:mt",
    jurisdiction_id="ocd-jurisdiction/country:us/state:mt/government",
    url="http://leg.mt.gov/",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=100,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:mt", "lower", 100
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=50,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:mt", "upper", 50
        ),
    ),
)
