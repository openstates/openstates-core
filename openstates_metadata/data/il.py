from ..models import State, Chamber

IL = State(
    name="Illinois",
    abbr="IL",
    capital="Springfield",
    capital_tz="America/Chicago",
    fips="17",
    unicameral=False,
    legislature_name="Illinois General Assembly",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=118,
        seats=None,
        division_ids=None,
        title="Representative",
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=59,
        seats=None,
        division_ids=None,
        title="Senator",
    ),
)
