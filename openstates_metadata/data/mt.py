from ..models import State, Chamber, District

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
        title="Representative",
        districts=None,
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=50,
        title="Senator",
        districts=None,
    ),
)
