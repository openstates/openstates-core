from ..models import State, Chamber, District

CA = State(
    name="California",
    abbr="CA",
    capital="Sacramento",
    capital_tz="America/Los_Angeles",
    fips="06",
    unicameral=False,
    legislature_name="California State Legislature",
    lower=Chamber(
        chamber_type="lower",
        name="Assembly",
        num_seats=80,
        title="Assemblymember",
        districts=None,
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=40,
        title="Senator",
        districts=None,
    ),
)
