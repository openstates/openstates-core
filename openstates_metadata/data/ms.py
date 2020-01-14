from ..models import State, Chamber, District

MS = State(
    name="Mississippi",
    abbr="MS",
    capital="Jackson",
    capital_tz="America/Chicago",
    fips="28",
    unicameral=False,
    legislature_name="Mississippi Legislature",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=122,
        title="Representative",
        districts=None,
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=52,
        title="Senator",
        districts=None,
    ),
)
