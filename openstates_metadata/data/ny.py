from ..models import State, Chamber, District

NY = State(
    name="New York",
    abbr="NY",
    capital="Albany",
    capital_tz="America/New_York",
    fips="36",
    unicameral=False,
    legislature_name="New York Legislature",
    lower=Chamber(
        chamber_type="lower",
        name="Assembly",
        num_seats=150,
        title="Assembly Member",
        districts=None,
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=63,
        title="Senator",
        districts=None,
    ),
)
