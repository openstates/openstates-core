from ..models import State, Chamber, simple_numbered_districts

IL = State(
    name="Illinois",
    abbr="IL",
    capital="Springfield",
    capital_tz="America/Chicago",
    fips="17",
    unicameral=False,
    legislature_name="Illinois General Assembly",
    division_id="ocd-division/country:us/state:il",
    jurisdiction_id="ocd-jurisdiction/country:us/state:il/government",
    url="http://www.ilga.gov/",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=118,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:il", "lower", 118
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=59,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:il", "upper", 59
        ),
    ),
)
