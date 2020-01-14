from ..models import State, Chamber

HI = State(
    name="Hawaii",
    abbr="HI",
    capital="Honolulu",
    capital_tz="Pacific/Honolulu",
    fips="15",
    unicameral=False,
    legislature_name="Hawaii State Legislature",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=51,
        seats=None,
        division_ids=None,
        title="Representative",
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=25,
        seats=None,
        division_ids=None,
        title="Senator",
    ),
)
