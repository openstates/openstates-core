from ..models import State, Chamber, simple_numbered_districts

ID = State(
    name="Idaho",
    abbr="ID",
    capital="Boise",
    capital_tz="America/Denver",
    fips="16",
    unicameral=False,
    legislature_name="Idaho State Legislature",
    division_id="ocd-division/country:us/state:id",
    jurisdiction_id="ocd-jurisdiction/country:us/state:id/government",
    url="http://www.legislature.idaho.gov",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=70,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:id", "lower", 35, num_seats=2
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=35,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:id", "upper", 35
        ),
    ),
)
