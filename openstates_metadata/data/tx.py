from ..models import State, Chamber

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
        seats=None,
        division_ids=None,
        title="Representative",
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=31,
        seats=None,
        division_ids=None,
        title="Senator",
    ),
)
