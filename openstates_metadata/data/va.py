from ..models import State, Chamber, simple_numbered_districts

VA = State(
    name="Virginia",
    abbr="VA",
    capital="Richmond",
    capital_tz="America/New_York",
    fips="51",
    unicameral=False,
    legislature_name="Virginia General Assembly",
    legislature_organization_id="ocd-organization/e56c1fc3-f311-4a51-a693-05c3e922f1b7",
    executive_name="Office of the Governor",
    executive_organization_id="ocd-organization/1251b370-e115-4240-bd6c-68bfe247050e",
    division_id="ocd-division/country:us/state:va",
    jurisdiction_id="ocd-jurisdiction/country:us/state:va/government",
    url="http://virginiageneralassembly.gov/",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        organization_id="ocd-organization/0c3daf42-2835-49cf-8f58-b1d771dae687",
        num_seats=100,
        title="Delegate",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:va", "lower", 100
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        organization_id="ocd-organization/9f1a0a17-d2fb-4d0c-90fb-119004411b83",
        num_seats=40,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:va", "upper", 40
        ),
    ),
)
