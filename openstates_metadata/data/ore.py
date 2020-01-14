from ..models import State, Chamber, District

OR = State(
    name="Oregon",
    abbr="OR",
    capital="Salem",
    capital_tz="America/Los_Angeles",
    fips="41",
    unicameral=False,
    legislature_name="Oregon Legislative Assembly",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=60,
        title="Representative",
        districts=None,
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=30,
        title="Senator",
        districts=None,
    ),
)
