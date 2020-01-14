from ..models import State, Chamber, simple_numbered_districts

OK = State(
    name="Oklahoma",
    abbr="OK",
    capital="Oklahoma City",
    capital_tz="America/Chicago",
    fips="40",
    unicameral=False,
    legislature_name="Oklahoma Legislature",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=101,
        title="Representative",
        districts=simple_numbered_districts(101),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=48,
        title="Senator",
        districts=simple_numbered_districts(48),
    ),
)
