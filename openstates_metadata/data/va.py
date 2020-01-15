from ..models import State, Chamber, simple_numbered_districts

VA = State(
    name="Virginia",
    abbr="VA",
    capital="Richmond",
    capital_tz="America/New_York",
    fips="51",
    unicameral=False,
    legislature_name="Virginia General Assembly",
    division_id="ocd-division/country:us/state:va",
    jurisdiction_id="ocd-jurisdiction/country:us/state:va/government",
    url="http://virginiageneralassembly.gov/",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=100,
        title="Delegate",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:va", "lower", 100
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=40,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:va", "upper", 40
        ),
    ),
)
