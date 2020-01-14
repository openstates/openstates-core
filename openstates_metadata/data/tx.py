from ..models import State, Chamber, District

TX = State(
    name="Texas",
    abbr="TX",
    capital="Austin",
    capital_tz="America/Chicago",
    fips="48",
    unicameral=False,
    legislature_name="Texas Legislature",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=150,
        title="Representative",
        districts=None,
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=31,
        title="Senator",
        districts=None,
    ),
)
