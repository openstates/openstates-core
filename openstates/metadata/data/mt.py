from ..models import State, Chamber, simple_numbered_districts

MT = State(
    name="Montana",
    abbr="MT",
    capital="Helena",
    capital_tz="America/Denver",
    fips="30",
    unicameral=False,
    legislature_name="Montana Legislature",
    legislature_organization_id="ocd-organization/803c558f-dec2-4f43-9c35-e73a6e849408",
    executive_name="Office of the Governor",
    executive_organization_id="ocd-organization/2838c5e6-e793-518d-a722-6140d5f8d0aa",
    division_id="ocd-division/country:us/state:mt",
    jurisdiction_id="ocd-jurisdiction/country:us/state:mt/government",
    url="http://leg.mt.gov/",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        organization_id="ocd-organization/7508efaf-3ca6-436d-8858-45b2f73a78d9",
        num_seats=100,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:mt", "lower", 100
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        organization_id="ocd-organization/1cf80fcd-e90e-4d0b-87d6-304fad2262f9",
        num_seats=50,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:mt", "upper", 50
        ),
    ),
)
