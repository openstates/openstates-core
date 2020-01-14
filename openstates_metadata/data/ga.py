from ..models import State, Chamber, District

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
        title="Representative",
        districts=None,
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=56,
        title="Senator",
        districts=None,
    ),
)
