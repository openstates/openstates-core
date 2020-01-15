from ..models import State, Chamber, simple_numbered_districts

ND = State(
    name="North Dakota",
    abbr="ND",
    capital="Bismarck",
    capital_tz="America/North_Dakota/Center",
    fips="38",
    unicameral=False,
    legislature_name="North Dakota Legislative Assembly",
    division_id="ocd-division/country:us/state:nd",
    jurisdiction_id="ocd-jurisdiction/country:us/state:nd/government",
    url="http://www.legis.nd.gov/",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=94,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:nd", "lower", 47, num_seats=2
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=47,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:nd", "upper", 47
        ),
    ),
)
