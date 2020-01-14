from ..models import State, Chamber

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
        seats=None,
        division_ids=None,
        title="Representative",
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=30,
        seats=None,
        division_ids=None,
        title="Senator",
    ),
)
