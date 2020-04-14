from ..models import State, Chamber, simple_numbered_districts

DE = State(
    name="Delaware",
    abbr="DE",
    capital="Dover",
    capital_tz="America/New_York",
    fips="10",
    unicameral=False,
    legislature_name="Delaware General Assembly",
    legislature_organization_id="ocd-organization/d2671846-0bc5-4082-b96d-989b31cc037f",
    executive_name="Office of the Governor",
    executive_organization_id="ocd-organization/dcfaf7fc-52ad-4a49-b88a-3a6fcea19248",
    division_id="ocd-division/country:us/state:de",
    jurisdiction_id="ocd-jurisdiction/country:us/state:de/government",
    url="http://legis.delaware.gov/",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        organization_id="ocd-organization/378d45a3-b3f9-41d5-b4f1-6fcf2979666c",
        num_seats=41,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:de", "lower", 41
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        organization_id="ocd-organization/099db7ce-13e0-4865-98ef-9787f65705c4",
        num_seats=21,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:de", "upper", 21
        ),
    ),
)
