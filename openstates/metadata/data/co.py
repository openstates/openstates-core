from ..models import State, Chamber, simple_numbered_districts

CO = State(
    name="Colorado",
    abbr="CO",
    capital="Denver",
    capital_tz="America/Denver",
    fips="08",
    unicameral=False,
    legislature_name="Colorado General Assembly",
    legislature_organization_id="ocd-organization/2fc73234-69ce-4a42-b85a-4a52a676e6e9",
    executive_name="Office of the Governor",
    executive_organization_id="ocd-organization/1f6f6532-1bc8-4ddb-8350-27fcd47c6795",
    division_id="ocd-division/country:us/state:co",
    jurisdiction_id="ocd-jurisdiction/country:us/state:co/government",
    url="http://leg.colorado.gov/",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        organization_id="ocd-organization/e047d0e5-2c93-4e39-bea3-04c0d9d11b20",
        num_seats=65,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:co", "lower", 65
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        organization_id="ocd-organization/98d43d46-9571-4a40-9007-581d84d41bb8",
        num_seats=35,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:co", "upper", 35
        ),
    ),
)
