from ..models import State, Chamber, District

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
        title="Representative",
        districts=None,
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=59,
        title="Senator",
        districts=None,
    ),
)
