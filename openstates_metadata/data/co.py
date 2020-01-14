from ..models import State, Chamber

CO = State(
    name="Colorado",
    abbr="CO",
    capital="Denver",
    capital_tz="America/Denver",
    fips="08",
    unicameral=False,
    legislature_name="Colorado General Assembly",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=65,
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
