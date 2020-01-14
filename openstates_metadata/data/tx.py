from ..models import State, Chamber, simple_numbered_districts

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
        districts=simple_numbered_districts(150),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=31,
        title="Senator",
        districts=simple_numbered_districts(31),
    ),
)
