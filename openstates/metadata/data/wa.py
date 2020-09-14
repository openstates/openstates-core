from ..models import State, Chamber, simple_numbered_districts

WA = State(
    name="Washington",
    abbr="WA",
    capital="Olympia",
    capital_tz="America/Los_Angeles",
    fips="53",
    unicameral=False,
    legislature_name="Washington State Legislature",
    legislature_organization_id="ocd-organization/a7819d04-7b5e-4d2e-b47f-5dca9f09fc81",
    executive_name="Office of the Governor",
    executive_organization_id="ocd-organization/cb29ec2f-1ee0-50b9-8394-f43504579f65",
    division_id="ocd-division/country:us/state:wa",
    jurisdiction_id="ocd-jurisdiction/country:us/state:wa/government",
    url="http://www.leg.wa.gov",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        organization_id="ocd-organization/7417a716-eba8-4437-a6e9-df14694bcb79",
        num_seats=98,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:wa", "lower", 49, num_seats=2
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        organization_id="ocd-organization/ddae63d3-9f3e-4c46-a00f-703fe21b54d1",
        num_seats=49,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:wa", "upper", 49
        ),
    ),
)
