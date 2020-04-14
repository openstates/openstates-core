from ..models import State, Chamber, simple_numbered_districts

TX = State(
    name="Texas",
    abbr="TX",
    capital="Austin",
    capital_tz="America/Chicago",
    fips="48",
    unicameral=False,
    legislature_name="Texas Legislature",
    legislature_organization_id="ocd-organization/8ab77a54-0646-413c-a63a-dc85154282b7",
    executive_name="Office of the Governor",
    executive_organization_id="ocd-organization/4c8c2a9c-f33c-476d-bf81-266eb72193f0",
    division_id="ocd-division/country:us/state:tx",
    jurisdiction_id="ocd-jurisdiction/country:us/state:tx/government",
    url="https://capitol.texas.gov/",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        organization_id="ocd-organization/d6189dbb-417e-429e-ae4b-2ee6747eddc0",
        num_seats=150,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:tx", "lower", 150
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        organization_id="ocd-organization/cabf1716-c572-406a-bfdd-1917c11ac629",
        num_seats=31,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:tx", "upper", 31
        ),
    ),
)
