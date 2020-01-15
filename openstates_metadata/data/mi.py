from ..models import State, Chamber, simple_numbered_districts

MI = State(
    name="Michigan",
    abbr="MI",
    capital="Lansing",
    capital_tz="America/New_York",
    fips="26",
    unicameral=False,
    legislature_name="Michigan Legislature",
    division_id="ocd-division/country:us/state:mi",
    jurisdiction_id="ocd-jurisdiction/country:us/state:mi/government",
    url="http://www.legislature.mi.gov",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=110,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:mi", "lower", 110
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=38,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:mi", "upper", 38
        ),
    ),
)
