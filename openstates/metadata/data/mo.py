from ..models import State, Chamber, simple_numbered_districts

MO = State(
    name="Missouri",
    abbr="MO",
    capital="Jefferson City",
    capital_tz="America/Chicago",
    fips="29",
    unicameral=False,
    legislature_name="Missouri General Assembly",
    legislature_organization_id="ocd-organization/997c6150-6c45-4178-82dd-e111c0029554",
    executive_name="Office of the Governor",
    executive_organization_id="ocd-organization/dd35cadb-0d6f-4a80-a84a-6ab08c2701b8",
    division_id="ocd-division/country:us/state:mo",
    jurisdiction_id="ocd-jurisdiction/country:us/state:mo/government",
    url="http://www.moga.mo.gov/",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        organization_id="ocd-organization/b028938f-599d-4b3a-8d53-fdb9de12e759",
        num_seats=163,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:mo", "lower", 163
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        organization_id="ocd-organization/8ff25b39-cd33-4cee-a2a9-d88b80b2c6fe",
        num_seats=34,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:mo", "upper", 34
        ),
    ),
)
