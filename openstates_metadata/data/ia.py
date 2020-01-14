from ..models import State, Chamber

IA = State(
    name="Iowa",
    abbr="IA",
    capital="Des Moines",
    capital_tz="America/Chicago",
    fips="19",
    unicameral=False,
    legislature_name="Iowa General Assembly",
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
