from ..models import State, Chamber, simple_numbered_districts

CT = State(
    name="Connecticut",
    abbr="CT",
    capital="Hartford",
    capital_tz="America/New_York",
    fips="09",
    unicameral=False,
    legislature_name="Connecticut General Assembly",
    legislature_organization_id="ocd-organization/474ab9de-3ab4-4294-88c1-43ffd506870a",
    executive_name="Office of the Governor",
    executive_organization_id="ocd-organization/76921ea9-d120-566d-9612-ac1b715d0e68",
    division_id="ocd-division/country:us/state:ct",
    jurisdiction_id="ocd-jurisdiction/country:us/state:ct/government",
    url="http://www.cga.ct.gov/",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        organization_id="ocd-organization/8e8c6d29-dcc1-4d2f-9ca5-82a4a3d3b962",
        num_seats=151,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:ct", "lower", 151
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        organization_id="ocd-organization/46a37f5a-a01b-4905-b023-a443b5be41c6",
        num_seats=36,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:ct", "upper", 36
        ),
    ),
)
