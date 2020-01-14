from ..models import State, Chamber, District

IA = State(
    name="Iowa",
    abbr="IA",
    capital="Des Moines",
    capital_tz="America/Chicago",
    fips="19",
    unicameral=False,
    legislature_name="Iowa General Assembly",
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