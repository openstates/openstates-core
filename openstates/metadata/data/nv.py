from ..models import State, Chamber, simple_numbered_districts

NV = State(
    name="Nevada",
    abbr="NV",
    capital="Carson City",
    capital_tz="America/Los_Angeles",
    fips="32",
    unicameral=False,
    legislature_name="Nevada Legislature",
    legislature_organization_id="ocd-organization/770c2aae-0332-4f24-a8e0-e0bf666dc992",
    executive_name="Office of the Governor",
    executive_organization_id="ocd-organization/0328f08e-ceb3-4d5c-a8d3-a73a3443e02e",
    division_id="ocd-division/country:us/state:nv",
    jurisdiction_id="ocd-jurisdiction/country:us/state:nv/government",
    url="http://www.leg.state.nv.us/",
    lower=Chamber(
        chamber_type="lower",
        name="Assembly",
        organization_id="ocd-organization/258cdef7-dac8-4ec1-8f74-00a70ee10269",
        num_seats=42,
        title="Assembly Member",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:nv", "lower", 42
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        organization_id="ocd-organization/c4400c7b-157d-442a-b688-543ffb989967",
        num_seats=21,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:nv", "upper", 21
        ),
    ),
)
