from ..models import State, Chamber

WY = State(
    name="Wyoming",
    abbr="WY",
    capital="Cheyenne",
    capital_tz="America/Denver",
    fips="56",
    unicameral=False,
    legislature_name="Wyoming State Legislature",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=60,
        seats=None,
        division_ids=None,
        title="Representative",
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=30,
        seats=None,
        division_ids=None,
        title="Senator",
    ),
)
