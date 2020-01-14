from ..models import State, Chamber, District

MO = State(
    name="Missouri",
    abbr="MO",
    capital="Jefferson City",
    capital_tz="America/Chicago",
    fips="29",
    unicameral=False,
    legislature_name="Missouri General Assembly",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=163,
        title="Representative",
        districts=None,
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=34,
        title="Senator",
        districts=None,
    ),
)
