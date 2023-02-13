from ..models import State, Chamber, simple_numbered_districts

AS = State(
    name="American Samoa",
    abbr="AS",
    capital="Pago Pago",
    capital_tz="Pacific/Samoa",
    fips="60",
    unicameral=False,
    url="https://www.americansamoa.gov",
    division_id="ocd-division/country:us/territory:as",
    jurisdiction_id="ocd-jurisdiction/country:us/territory:as/government",
    legislature_name="American Samoa Fono",
    legislature_organization_id="ocd-organization/739d2a37-30aa-46ca-a0ce-41bdd9f39f51",
    executive_name="Governor of American Samoa",
    executive_organization_id="ocd-organization/1b28142e-dcb4-457e-b17a-11298ae7ccf8",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        organization_id="ocd-organization/f6355e28-9d90-4fa2-8e58-8429a5d0e2a3",
        num_seats=21,
        title="Legislators",
        districts=simple_numbered_districts(
            "ocd-division/country:us/territory:as", "lower", 21
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        organization_id="ocd-organization/9a527967-b7f1-4186-a635-611a1f29dd1d",
        num_seats=18,
        title="Legislators",
        districts=simple_numbered_districts(
            "ocd-division/country:us/territory:as", "upper", 18
        ),
    ),
)
