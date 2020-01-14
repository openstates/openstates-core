from ..models import State, Chamber

FL = State(
    name="Florida",
    abbr="FL",
    capital="Tallahassee",
    capital_tz="America/New_York",
    fips="12",
    unicameral=False,
    legislature_name="Florida Legislature",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=120,
        seats=None,
        division_ids=None,
        title="Representative",
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=40,
        seats=None,
        division_ids=None,
        title="Senator",
    ),
)
