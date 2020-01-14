from ..models import State, Chamber

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
        seats=None,
        division_ids=None,
        title="Representative",
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=52,
        seats=None,
        division_ids=None,
        title="Senator",
    ),
)
