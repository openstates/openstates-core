from ..models import State, Chamber

KY = State(
    name="Kentucky",
    abbr="KY",
    capital="Frankfort",
    capital_tz="America/New_York",
    fips="21",
    unicameral=False,
    legislature_name="Kentucky General Assembly",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=100,
        seats=None,
        division_ids=None,
        title="Representative",
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=38,
        seats=None,
        division_ids=None,
        title="Senator",
    ),
)
