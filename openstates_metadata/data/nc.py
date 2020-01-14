from ..models import State, Chamber, District

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
        title="Representative",
        districts=None,
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=50,
        title="Senator",
        districts=None,
    ),
)
