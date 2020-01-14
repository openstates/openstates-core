from ..models import State, Chamber, District

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
        districts=None,
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=25,
        title="Senator",
        districts=None,
    ),
)
