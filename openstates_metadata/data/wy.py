from ..models import State, Chamber, District

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
        districts=None,
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=30,
        title="Senator",
        districts=None,
    ),
)
