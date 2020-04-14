from ..models import State, Chamber, simple_numbered_districts

GA = State(
    name="Georgia",
    abbr="GA",
    capital="Atlanta",
    capital_tz="America/New_York",
    fips="13",
    unicameral=False,
    legislature_name="Georgia General Assembly",
    legislature_organization_id="ocd-organization/1186f244-c9f8-46de-a453-c58d6de050d7",
    executive_name="Office of the Governor",
    executive_organization_id="ocd-organization/f35a01bf-5beb-5437-9842-e5ba89734908",
    division_id="ocd-division/country:us/state:ga",
    jurisdiction_id="ocd-jurisdiction/country:us/state:ga/government",
    url="http://www.legis.ga.gov/",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        organization_id="ocd-organization/f94ae35f-f161-4599-b603-e7737dc8c93f",
        num_seats=180,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:ga", "lower", 180
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        organization_id="ocd-organization/3b9777f2-c2fb-48e1-83bf-66fc7a17492e",
        num_seats=56,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:ga", "upper", 56
        ),
    ),
)
