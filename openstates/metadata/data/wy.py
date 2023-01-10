from ..models import State, Chamber, simple_numbered_districts

WY = State(
    name="Wyoming",
    abbr="WY",
    capital="Cheyenne",
    capital_tz="America/Denver",
    fips="56",
    unicameral=False,
    legislature_name="Wyoming State Legislature",
    legislature_organization_id="ocd-organization/b47d8d36-68d9-4bf0-807a-5b9c9ed2d99f",
    executive_name="Office of the Governor",
    executive_organization_id="ocd-organization/ef8bc870-8b19-4f99-a410-310d0ead92f4",
    division_id="ocd-division/country:us/state:wy",
    jurisdiction_id="ocd-jurisdiction/country:us/state:wy/government",
    url="http://legisweb.state.wy.us/",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        organization_id="ocd-organization/683ca907-05d4-4c84-8d7b-f04f73e295ad",
        num_seats=62,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:wy", "lower", 62
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        organization_id="ocd-organization/6e0e804b-be2d-408b-9dc4-d8e3739915bd",
        num_seats=31,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:wy", "upper", 31
        ),
    ),
)
