from ..models import State, Chamber, District

KY = State(
    name="Kentucky",
    abbr="KY",
    capital="Frankfort",
    capital_tz="America/New_York",
    fips="21",
    unicameral=False,
    legislature_name="Kentucky General Assembly",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=100,
        title="Representative",
        districts=None,
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=38,
        title="Senator",
        districts=None,
    ),
)
