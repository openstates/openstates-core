from ..models import State, Chamber

NV = State(
    name="Nevada",
    abbr="NV",
    capital="Carson City",
    capital_tz="America/Los_Angeles",
    fips="32",
    unicameral=False,
    legislature_name="Nevada Legislature",
    lower=Chamber(
        chamber_type="lower",
        name="Assembly",
        num_seats=42,
        seats=None,
        division_ids=None,
        title="Assembly Member",
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=21,
        seats=None,
        division_ids=None,
        title="Senator",
    ),
)
