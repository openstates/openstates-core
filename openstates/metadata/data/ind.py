from ..models import State, Chamber, simple_numbered_districts

IN = State(
    name="Indiana",
    abbr="IN",
    capital="Indianapolis",
    capital_tz="America/Indiana/Indianapolis",
    fips="18",
    unicameral=False,
    legislature_name="Indiana General Assembly",
    legislature_organization_id="ocd-organization/7de4a037-2e98-46d0-975c-67d42eaff437",
    executive_name="Office of the Governor",
    executive_organization_id="ocd-organization/3ecd0c76-5e2c-4e7c-9882-615d64fd0f47",
    division_id="ocd-division/country:us/state:in",
    jurisdiction_id="ocd-jurisdiction/country:us/state:in/government",
    url="http://www.in.gov/",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        organization_id="ocd-organization/10bc85d1-df30-4bb9-a8d0-e158225b4431",
        num_seats=100,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:in", "lower", 100
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        organization_id="ocd-organization/b8946e05-f621-442a-8352-cc51db92980c",
        num_seats=50,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:in", "upper", 50
        ),
    ),
)
