from ..models import State, Chamber, simple_numbered_districts

HI = State(
    name="Hawaii",
    abbr="HI",
    capital="Honolulu",
    capital_tz="Pacific/Honolulu",
    fips="15",
    unicameral=False,
    legislature_name="Hawaii State Legislature",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=51,
        title="Representative",
        districts=simple_numbered_districts(51),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=25,
        title="Senator",
        districts=simple_numbered_districts(25),
    ),
)
