from ..models import State, Chamber

WI = State(
    name="Wisconsin",
    abbr="WI",
    capital="Madison",
    capital_tz="America/Chicago",
    fips="55",
    unicameral=False,
    legislature_name="Wisconsin State Legislature",
    lower=Chamber(
        chamber_type="lower",
        name="Assembly",
        num_seats=99,
        seats=None,
        division_ids=None,
        title="Representative",
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=33,
        seats=None,
        division_ids=None,
        title="Senator",
    ),
)
