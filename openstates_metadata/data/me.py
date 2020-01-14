from ..models import State, Chamber, simple_numbered_districts

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
        title="Representative",
        districts=simple_numbered_districts(151),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=35,
        title="Senator",
        districts=simple_numbered_districts(35),
    ),
)
