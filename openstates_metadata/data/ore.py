from ..models import State, Chamber, simple_numbered_districts

OR = State(
    name="Oregon",
    abbr="OR",
    capital="Salem",
    capital_tz="America/Los_Angeles",
    fips="41",
    unicameral=False,
    legislature_name="Oregon Legislative Assembly",
    division_id="ocd-division/country:us/state:or",
    jurisdiction_id="ocd-jurisdiction/country:us/state:or/government",
    url="https://olis.leg.state.or.us",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=60,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:or", "lower", 60
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=30,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:or", "upper", 30
        ),
    ),
)
