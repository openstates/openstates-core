from ..models import State, Chamber, simple_numbered_districts

NM = State(
    name="New Mexico",
    abbr="NM",
    capital="Santa Fe",
    capital_tz="America/Chicago",
    fips="35",
    unicameral=False,
    legislature_name="New Mexico Legislature",
    division_id="ocd-division/country:us/state:nm",
    jurisdiction_id="ocd-jurisdiction/country:us/state:nm/government",
    url="https://www.nmlegis.gov",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=70,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:nm", "lower", 70
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=42,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:nm", "upper", 42
        ),
    ),
)
