from ..models import State, Chamber

TN = State(
    name="Tennessee",
    abbr="TN",
    capital="Nashville",
    capital_tz="America/Chicago",
    fips="47",
    unicameral=False,
    legislature_name="Tennessee General Assembly",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=99,
        seats=None,
        division_ids=None,
        title="Representative",
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=33,
        seats=None,
        division_ids=None,
        title="Senator",
    ),
)
