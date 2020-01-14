from ..models import State, Chamber

AL = State(
    name="Alabama",
    abbr="AL",
    capital="Montgomery",
    capital_tz="America/Chicago",
    fips="01",
    unicameral=False,
    legislature_name="Alabama Legislature",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=105,
        seats=None,
        division_ids=None,
        title="Representative",
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=35,
        seats=None,
        division_ids=None,
        title="Senator",
    ),
)
