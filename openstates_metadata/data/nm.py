from ..models import State, Chamber, District

NM = State(
    name="New Mexico",
    abbr="NM",
    capital="Santa Fe",
    capital_tz="America/Chicago",
    fips="35",
    unicameral=False,
    legislature_name="New Mexico Legislature",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=70,
        title="Representative",
        districts=None,
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=42,
        title="Senator",
        districts=None,
    ),
)
