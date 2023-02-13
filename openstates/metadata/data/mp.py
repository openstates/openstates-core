from ..models import State, Chamber, simple_numbered_districts

MP = State(
    name="Northern Mariana Islands",
    abbr="MP",
    capital="Saipan",
    capital_tz="Pacific/Guam",
    fips="69",
    unicameral=False,
    # 2023-02-13 -> site is a default nginx page
    url="https://gov.mp",
    legislature_name="Northern Marianas Commonwealth Legislature",
    legislature_organization_id="ocd-organization/3266e4a2-cfa7-425a-92d3-8b18e78f0cf5",
    executive_name="Office of Governor",
    executive_organization_id="ocd-organization/568c13c8-d87b-40f0-a4a5-f1543e5f9089",
    division_id="ocd-division/country:us/territory:mp",
    jurisdiction_id="ocd-jurisdiction/country:us/territory:mp/government",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        organization_id="ocd-organization/58222d00-3b6f-422e-9b34-81350338ae91",
        num_seats=20,
        title="Legislators",
        districts=simple_numbered_districts(
            "ocd-division/country:us/territory:mp", "lower", 20
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        organization_id="ocd-organization/9f00690c-2f99-4ed0-8d0c-feadfc058054",
        num_seats=9,
        title="Senators",
        districts=simple_numbered_districts(
            "ocd-division/country:us/territory:mp", "upper", 9
        ),
    ),
)
