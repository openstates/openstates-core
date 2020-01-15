from ..models import State, Chamber, simple_numbered_districts

CA = State(
    name="California",
    abbr="CA",
    capital="Sacramento",
    capital_tz="America/Los_Angeles",
    fips="06",
    unicameral=False,
    legislature_name="California State Legislature",
    division_id="ocd-division/country:us/state:ca",
    jurisdiction_id="ocd-jurisdiction/country:us/state:ca/government",
    url="http://www.legislature.ca.gov/",
    lower=Chamber(
        chamber_type="lower",
        name="Assembly",
        num_seats=80,
        title="Assemblymember",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:ca", "lower", 80
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=40,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:ca", "upper", 40
        ),
    ),
)
