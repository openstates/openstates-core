from ..models import State, Chamber

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
        seats=None,
        division_ids=None,
        title="Representative",
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=50,
        seats=None,
        division_ids=None,
        title="Senator",
    ),
)
