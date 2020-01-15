from ..models import State, Chamber, simple_numbered_districts

WI = State(
    name="Wisconsin",
    abbr="WI",
    capital="Madison",
    capital_tz="America/Chicago",
    fips="55",
    unicameral=False,
    legislature_name="Wisconsin State Legislature",
    division_id="ocd-division/country:us/state:wi",
    jurisdiction_id="ocd-jurisdiction/country:us/state:wi/government",
    url="http://legis.wisconsin.gov/",
    lower=Chamber(
        chamber_type="lower",
        name="Assembly",
        num_seats=99,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:wi", "lower", 99
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=33,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:wi", "upper", 33
        ),
    ),
)
