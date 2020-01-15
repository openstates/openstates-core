from ..models import State, Chamber, simple_numbered_districts

UT = State(
    name="Utah",
    abbr="UT",
    capital="Salt Lake City",
    capital_tz="America/Denver",
    fips="49",
    unicameral=False,
    legislature_name="Utah State Legislature",
    division_id="ocd-division/country:us/state:ut",
    jurisdiction_id="ocd-jurisdiction/country:us/state:ut/government",
    url="http://le.utah.gov/",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=75,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:ut", "lower", 75
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=29,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:ut", "upper", 29
        ),
    ),
)
