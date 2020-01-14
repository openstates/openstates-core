from ..models import State, Chamber, District

AR = State(
    name="Arkansas",
    abbr="AR",
    capital="Little Rock",
    capital_tz="America/Chicago",
    fips="05",
    unicameral=False,
    legislature_name="Arkansas General Assembly",
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
        num_seats=35,
        title="Senator",
        districts=None,
    ),
)
