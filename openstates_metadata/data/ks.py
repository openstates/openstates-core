from ..models import State, Chamber

KS = State(
    name="Kansas",
    abbr="KS",
    capital="Topeka",
    capital_tz="America/Chicago",
    fips="20",
    unicameral=False,
    legislature_name="Kansas State Legislature",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=125,
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
