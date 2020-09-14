from ..models import State, Chamber, simple_numbered_districts

IL = State(
    name="Illinois",
    abbr="IL",
    capital="Springfield",
    capital_tz="America/Chicago",
    fips="17",
    unicameral=False,
    legislature_name="Illinois General Assembly",
    legislature_organization_id="ocd-organization/52332da7-9146-412e-bf64-a291e2757b63",
    executive_name="Office of the Governor",
    executive_organization_id="ocd-organization/1cc0938a-ec95-595c-ada8-3c9379af4704",
    division_id="ocd-division/country:us/state:il",
    jurisdiction_id="ocd-jurisdiction/country:us/state:il/government",
    url="http://www.ilga.gov/",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        organization_id="ocd-organization/76120f9a-2982-4cc5-a6e2-de7401fa0d38",
        num_seats=118,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:il", "lower", 118
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        organization_id="ocd-organization/20782ae5-cc22-4470-846b-fd9788ad3db7",
        num_seats=59,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:il", "upper", 59
        ),
    ),
)
