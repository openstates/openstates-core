from ..models import State, Chamber

SC = State(
    name="South Carolina",
    abbr="SC",
    capital="Columbia",
    capital_tz="America/New_York",
    fips="45",
    unicameral=False,
    legislature_name="South Carolina Legislature",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=124,
        seats=None,
        division_ids=None,
        title="Representative",
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=46,
        seats=None,
        division_ids=None,
        title="Senator",
    ),
)
