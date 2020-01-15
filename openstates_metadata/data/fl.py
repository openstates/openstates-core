from ..models import State, Chamber, simple_numbered_districts

FL = State(
    name="Florida",
    abbr="FL",
    capital="Tallahassee",
    capital_tz="America/New_York",
    fips="12",
    unicameral=False,
    legislature_name="Florida Legislature",
    division_id="ocd-division/country:us/state:fl",
    jurisdiction_id="ocd-jurisdiction/country:us/state:fl/government",
    url="http://myflorida.com",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=120,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:fl", "lower", 120
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=40,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:fl", "upper", 40
        ),
    ),
)
