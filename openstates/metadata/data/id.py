from ..models import State, Chamber, simple_numbered_districts

ID = State(
    name="Idaho",
    abbr="ID",
    capital="Boise",
    capital_tz="America/Denver",
    fips="16",
    unicameral=False,
    legislature_name="Idaho State Legislature",
    legislature_organization_id="ocd-organization/654d4d38-e413-4307-a420-6f1ee2594673",
    executive_name="Office of the Governor",
    executive_organization_id="ocd-organization/9bbaab73-ae4e-5d25-9f32-c3af64a77829",
    division_id="ocd-division/country:us/state:id",
    jurisdiction_id="ocd-jurisdiction/country:us/state:id/government",
    url="http://www.legislature.idaho.gov",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        organization_id="ocd-organization/7a59916c-201a-49b2-9288-776ffea9f6cb",
        num_seats=70,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:id", "lower", 35, num_seats=2
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        organization_id="ocd-organization/e8c4c8ae-7ba0-4116-9865-5d34fcc6e681",
        num_seats=35,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:id", "upper", 35
        ),
    ),
)
