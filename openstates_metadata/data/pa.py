from ..models import State, Chamber, District

PA = State(
    name="Pennsylvania",
    abbr="PA",
    capital="Harrisburg",
    capital_tz="America/New_York",
    fips="42",
    unicameral=False,
    legislature_name="Pennsylvania General Assembly",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=203,
        title="Representative",
        districts=None,
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=50,
        title="Senator",
        districts=None,
    ),
)
