from ..models import State, Chamber, simple_numbered_districts

CO = State(
    name="Colorado",
    abbr="CO",
    capital="Denver",
    capital_tz="America/Denver",
    fips="08",
    unicameral=False,
    legislature_name="Colorado General Assembly",
    division_id="ocd-division/country:us/state:co",
    jurisdiction_id="ocd-jurisdiction/country:us/state:co/government",
    url="http://leg.colorado.gov/",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=65,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:co", "lower", 65
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=35,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:co", "upper", 35
        ),
    ),
)
