from ..models import State, Chamber, District

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
        title="Representative",
        districts=None,
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=33,
        title="Senator",
        districts=None,
    ),
)
