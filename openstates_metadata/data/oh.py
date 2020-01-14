from ..models import State, Chamber

OH = State(
    name="Ohio",
    abbr="OH",
    capital="Columbus",
    capital_tz="America/New_York",
    fips="39",
    unicameral=False,
    legislature_name="Ohio General Assembly",
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
