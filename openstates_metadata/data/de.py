from ..models import State, Chamber

DE = State(
    name="Delaware",
    abbr="DE",
    capital="Dover",
    capital_tz="America/New_York",
    fips="10",
    unicameral=False,
    legislature_name="Delaware General Assembly",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=41,
        seats=None,
        division_ids=None,
        title="Representative",
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=21,
        seats=None,
        division_ids=None,
        title="Senator",
    ),
)
