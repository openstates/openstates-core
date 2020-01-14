from ..models import State, Chamber

CT = State(
    name="Connecticut",
    abbr="CT",
    capital="Hartford",
    capital_tz="America/New_York",
    fips="09",
    unicameral=False,
    legislature_name="Connecticut General Assembly",
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
        num_seats=36,
        seats=None,
        division_ids=None,
        title="Senator",
    ),
)
