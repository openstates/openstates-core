from ..models import State, Chamber

MT = State(
    name="Montana",
    abbr="MT",
    capital="Helena",
    capital_tz="America/Denver",
    fips="30",
    unicameral=False,
    legislature_name="Montana Legislature",
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
        num_seats=50,
        seats=None,
        division_ids=None,
        title="Senator",
    ),
)
