from ..models import State, Chamber, simple_numbered_districts

KS = State(
    name="Kansas",
    abbr="KS",
    capital="Topeka",
    capital_tz="America/Chicago",
    fips="20",
    unicameral=False,
    legislature_name="Kansas State Legislature",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=125,
        title="Representative",
        districts=simple_numbered_districts(125),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=40,
        title="Senator",
        districts=simple_numbered_districts(40),
    ),
)
