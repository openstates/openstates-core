from ..models import State, Chamber, simple_numbered_districts

RI = State(
    name="Rhode Island",
    abbr="RI",
    capital="Providence",
    capital_tz="America/New_York",
    fips="44",
    unicameral=False,
    legislature_name="Rhode Island General Assembly",
    legislature_organization_id="ocd-organization/fce467b7-470b-41c2-be23-0ed00804b512",
    executive_name="Office of the Governor",
    executive_organization_id="ocd-organization/3c6b003d-47bf-44ca-a3cf-fe7a53780cc8",
    division_id="ocd-division/country:us/state:ri",
    jurisdiction_id="ocd-jurisdiction/country:us/state:ri/government",
    url="http://www.ri.gov/",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        organization_id="ocd-organization/ba73a081-69ab-42c3-bf47-7620fec808cf",
        num_seats=75,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:ri", "lower", 75
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        organization_id="ocd-organization/bea6e1af-6d6b-4a81-8040-499daf785244",
        num_seats=38,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:ri", "upper", 38
        ),
    ),
)
