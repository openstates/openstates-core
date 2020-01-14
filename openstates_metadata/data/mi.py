from ..models import State, Chamber

MI = State(
    name="Michigan",
    abbr="MI",
    capital="Lansing",
    capital_tz="America/New_York",
    fips="26",
    unicameral=False,
    legislature_name="Michigan Legislature",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=110,
        seats=None,
        division_ids=None,
        title="Representative",
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=38,
        seats=None,
        division_ids=None,
        title="Senator",
    ),
)
