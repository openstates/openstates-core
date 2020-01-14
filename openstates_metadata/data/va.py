from ..models import State, Chamber, District

VA = State(
    name="Virginia",
    abbr="VA",
    capital="Richmond",
    capital_tz="America/New_York",
    fips="51",
    unicameral=False,
    legislature_name="Virginia General Assembly",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=100,
        title="Delegate",
        districts=None,
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=40,
        title="Senator",
        districts=None,
    ),
)