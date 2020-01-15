from ..models import State, Chamber, simple_numbered_districts

OH = State(
    name="Ohio",
    abbr="OH",
    capital="Columbus",
    capital_tz="America/New_York",
    fips="39",
    unicameral=False,
    legislature_name="Ohio General Assembly",
    division_id="ocd-division/country:us/state:oh",
    jurisdiction_id="ocd-jurisdiction/country:us/state:oh/government",
    url="http://www.legislature.state.oh.us/",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=99,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:oh", "lower", 99
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=33,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:oh", "upper", 33
        ),
    ),
)
