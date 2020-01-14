from ..models import State, Chamber, simple_numbered_districts

GA = State(
    name="Georgia",
    abbr="GA",
    capital="Atlanta",
    capital_tz="America/New_York",
    fips="13",
    unicameral=False,
    legislature_name="Georgia General Assembly",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=180,
        title="Representative",
        districts=simple_numbered_districts(180),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=56,
        title="Senator",
        districts=simple_numbered_districts(56),
    ),
)
