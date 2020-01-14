from ..models import State, Chamber

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
        seats=None,
        division_ids=None,
        title="Representative",
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=39,
        seats=None,
        division_ids=None,
        title="Senator",
    ),
)
