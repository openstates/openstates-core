from ..models import State, Chamber, simple_numbered_districts

MO = State(
    name="Missouri",
    abbr="MO",
    capital="Jefferson City",
    capital_tz="America/Chicago",
    fips="29",
    unicameral=False,
    legislature_name="Missouri General Assembly",
    division_id="ocd-division/country:us/state:mo",
    jurisdiction_id="ocd-jurisdiction/country:us/state:mo/government",
    url="http://www.moga.mo.gov/",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=163,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:mo", "lower", 163
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=34,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:mo", "upper", 34
        ),
    ),
)
