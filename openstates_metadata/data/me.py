from ..models import State, Chamber

ME = State(
    name="Maine",
    abbr="ME",
    capital="Augusta",
    capital_tz="America/New_York",
    fips="23",
    unicameral=False,
    legislature_name="Maine Legislature",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=151,
        seats=None,
        division_ids=None,
        title="Representative",
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=35,
        seats=None,
        division_ids=None,
        title="Senator",
    ),
)
