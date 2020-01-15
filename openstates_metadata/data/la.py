from ..models import State, Chamber, simple_numbered_districts

LA = State(
    name="Louisiana",
    abbr="LA",
    capital="Baton Rouge",
    capital_tz="America/Chicago",
    fips="22",
    unicameral=False,
    legislature_name="Louisiana Legislature",
    division_id="ocd-division/country:us/state:la",
    jurisdiction_id="ocd-jurisdiction/country:us/state:la/government",
    url="http://www.legis.la.gov/",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=105,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:la", "lower", 105
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=39,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:la", "upper", 39
        ),
    ),
)
