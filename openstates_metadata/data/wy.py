from ..models import State, Chamber, simple_numbered_districts

WY = State(
    name="Wyoming",
    abbr="WY",
    capital="Cheyenne",
    capital_tz="America/Denver",
    fips="56",
    unicameral=False,
    legislature_name="Wyoming State Legislature",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=60,
        title="Representative",
        districts=simple_numbered_districts(60),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=30,
        title="Senator",
        districts=simple_numbered_districts(30),
    ),
)
