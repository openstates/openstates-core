from ..models import State, Chamber, simple_numbered_districts

OK = State(
    name="Oklahoma",
    abbr="OK",
    capital="Oklahoma City",
    capital_tz="America/Chicago",
    fips="40",
    unicameral=False,
    legislature_name="Oklahoma Legislature",
    division_id="ocd-division/country:us/state:ok",
    jurisdiction_id="ocd-jurisdiction/country:us/state:ok/government",
    url="http://www.oklegislature.gov/",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=101,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:ok", "lower", 101
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=48,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:ok", "upper", 48
        ),
    ),
)
