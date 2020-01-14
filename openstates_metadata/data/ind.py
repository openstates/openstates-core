from ..models import State, Chamber, District

IN = State(
    name="Indiana",
    abbr="IN",
    capital="Indianapolis",
    capital_tz="America/Indiana/Indianapolis",
    fips="18",
    unicameral=False,
    legislature_name="Indiana General Assembly",
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
        num_seats=50,
        title="Senator",
        districts=None,
    ),
)
