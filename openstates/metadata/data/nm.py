from ..models import State, Chamber, simple_numbered_districts

NM = State(
    name="New Mexico",
    abbr="NM",
    capital="Santa Fe",
    capital_tz="America/Denver",
    fips="35",
    unicameral=False,
    legislature_name="New Mexico Legislature",
    legislature_organization_id="ocd-organization/7a5a12b7-e955-4999-a469-df3748934953",
    executive_name="Office of the Governor",
    executive_organization_id="ocd-organization/36f78a21-d16b-42a3-9b14-5265b4ebf59e",
    division_id="ocd-division/country:us/state:nm",
    jurisdiction_id="ocd-jurisdiction/country:us/state:nm/government",
    url="https://www.nmlegis.gov",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        organization_id="ocd-organization/af9a59f2-c6b2-4bb1-b270-85f5d40605b4",
        num_seats=70,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:nm", "lower", 70
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        organization_id="ocd-organization/a6719ff4-d604-4144-95e3-453a03672dfd",
        num_seats=42,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:nm", "upper", 42
        ),
    ),
)
