from ..models import State, Chamber, simple_numbered_districts

MS = State(
    name="Mississippi",
    abbr="MS",
    capital="Jackson",
    capital_tz="America/Chicago",
    fips="28",
    unicameral=False,
    legislature_name="Mississippi Legislature",
    division_id="ocd-division/country:us/state:ms",
    jurisdiction_id="ocd-jurisdiction/country:us/state:ms/government",
    url="http://www.legislature.ms.gov/",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=122,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:ms", "lower", 122
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=52,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:ms", "upper", 52
        ),
    ),
)
