from ..models import State, Chamber, District

RI = State(
    name="Rhode Island",
    abbr="RI",
    capital="Providence",
    capital_tz="America/New_York",
    fips="44",
    unicameral=False,
    legislature_name="Rhode Island General Assembly",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=75,
        title="Representative",
        districts=None,
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=38,
        title="Senator",
        districts=None,
    ),
)