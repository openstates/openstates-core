from ..models import State, Chamber, simple_numbered_districts

WI = State(
    name="Wisconsin",
    abbr="WI",
    capital="Madison",
    capital_tz="America/Chicago",
    fips="55",
    unicameral=False,
    legislature_name="Wisconsin State Legislature",
    legislature_organization_id="ocd-organization/1cba9936-eb76-4465-acb5-50c93cd4e8c9",
    executive_name="Office of the Governor",
    executive_organization_id="ocd-organization/791f3d9d-86c8-565a-b286-c996e8bcb17e",
    division_id="ocd-division/country:us/state:wi",
    jurisdiction_id="ocd-jurisdiction/country:us/state:wi/government",
    url="http://legis.wisconsin.gov/",
    lower=Chamber(
        chamber_type="lower",
        name="Assembly",
        organization_id="ocd-organization/2d0dada5-8153-44aa-b436-c92a90db0a9e",
        num_seats=99,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:wi", "lower", 99
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        organization_id="ocd-organization/c8a757e6-378e-468c-a526-e81ca083124b",
        num_seats=33,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:wi", "upper", 33
        ),
    ),
)
