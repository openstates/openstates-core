from ..models import State, Chamber

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
