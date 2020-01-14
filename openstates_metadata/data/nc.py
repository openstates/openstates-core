from ..models import State, Chamber

NC = State(
    name="North Carolina",
    abbr="NC",
    capital="Raleigh",
    capital_tz="America/New_York",
    fips="37",
    unicameral=False,
    legislature_name="North Carolina General Assembly",
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
        num_seats=50,
        seats=None,
        division_ids=None,
        title="Senator",
    ),
)
