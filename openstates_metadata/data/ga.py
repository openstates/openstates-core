from ..models import State, Chamber

GA = State(
    name="Georgia",
    abbr="GA",
    capital="Atlanta",
    capital_tz="America/New_York",
    fips="13",
    unicameral=False,
    legislature_name="Georgia General Assembly",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=180,
        seats=None,
        division_ids=None,
        title="Representative",
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=56,
        seats=None,
        division_ids=None,
        title="Senator",
    ),
)
