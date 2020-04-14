from ..models import State, Chamber, simple_numbered_districts

KY = State(
    name="Kentucky",
    abbr="KY",
    capital="Frankfort",
    capital_tz="America/New_York",
    fips="21",
    unicameral=False,
    legislature_name="Kentucky General Assembly",
    legislature_organization_id="ocd-organization/b5a82ff4-4fd3-41c8-bb44-32ad2e499482",
    executive_name="Office of the Governor",
    executive_organization_id="ocd-organization/d98917f5-3395-595e-b2d9-873936707342",
    division_id="ocd-division/country:us/state:ky",
    jurisdiction_id="ocd-jurisdiction/country:us/state:ky/government",
    url="http://www.lrc.ky.gov/",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        organization_id="ocd-organization/4e2398aa-4ffd-4e2c-8089-7a0cb64f1bc9",
        num_seats=100,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:ky", "lower", 100
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        organization_id="ocd-organization/523aa254-9d04-4641-9770-6488b5f4fb0e",
        num_seats=38,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:ky", "upper", 38
        ),
    ),
)
