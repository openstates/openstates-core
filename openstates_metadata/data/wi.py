from ..models import State, Chamber, District

WI = State(
    name="Wisconsin",
    abbr="WI",
    capital="Madison",
    capital_tz="America/Chicago",
    fips="55",
    unicameral=False,
    legislature_name="Wisconsin State Legislature",
    lower=Chamber(
        chamber_type="lower",
        name="Assembly",
        num_seats=99,
        title="Representative",
        districts=None,
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=33,
        title="Senator",
        districts=None,
    ),
)
