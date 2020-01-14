from ..models import State, Chamber, District

NV = State(
    name="Nevada",
    abbr="NV",
    capital="Carson City",
    capital_tz="America/Los_Angeles",
    fips="32",
    unicameral=False,
    legislature_name="Nevada Legislature",
    lower=Chamber(
        chamber_type="lower",
        name="Assembly",
        num_seats=42,
        title="Assembly Member",
        districts=None,
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=21,
        title="Senator",
        districts=None,
    ),
)
