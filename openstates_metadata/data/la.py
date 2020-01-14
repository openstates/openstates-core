from ..models import State, Chamber, District

LA = State(
    name="Louisiana",
    abbr="LA",
    capital="Baton Rouge",
    capital_tz="America/Chicago",
    fips="22",
    unicameral=False,
    legislature_name="Louisiana Legislature",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=105,
        title="Representative",
        districts=None,
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=39,
        title="Senator",
        districts=None,
    ),
)
