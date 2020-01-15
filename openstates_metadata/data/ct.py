from ..models import State, Chamber, simple_numbered_districts

CT = State(
    name="Connecticut",
    abbr="CT",
    capital="Hartford",
    capital_tz="America/New_York",
    fips="09",
    unicameral=False,
    legislature_name="Connecticut General Assembly",
    division_id="ocd-division/country:us/state:ct",
    jurisdiction_id="ocd-jurisdiction/country:us/state:ct/government",
    url="http://www.cga.ct.gov/",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=151,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:ct", "lower", 151
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=36,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:ct", "upper", 36
        ),
    ),
)
