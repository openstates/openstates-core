from ..models import State, Chamber, District

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
        districts=None,
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=48,
        title="Senator",
        districts=None,
    ),
)
