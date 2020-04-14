from ..models import State, Chamber, simple_numbered_districts

MS = State(
    name="Mississippi",
    abbr="MS",
    capital="Jackson",
    capital_tz="America/Chicago",
    fips="28",
    unicameral=False,
    legislature_name="Mississippi Legislature",
    legislature_organization_id="ocd-organization/f2b7fee5-8da1-431d-8ea1-19b7709194cc",
    executive_name="Office of the Governor",
    executive_organization_id="ocd-organization/2d23c3ec-897d-4ef8-85a5-0acb24328d5f",
    division_id="ocd-division/country:us/state:ms",
    jurisdiction_id="ocd-jurisdiction/country:us/state:ms/government",
    url="http://www.legislature.ms.gov/",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        organization_id="ocd-organization/47c2e037-ffe3-46c3-9399-8feb1f7d4988",
        num_seats=122,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:ms", "lower", 122
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        organization_id="ocd-organization/7e3c07c9-91ff-4445-8cef-57f85ab6ae9f",
        num_seats=52,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:ms", "upper", 52
        ),
    ),
)
