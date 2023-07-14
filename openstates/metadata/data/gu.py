from ..models import State, Chamber, simple_numbered_districts

GU = State(
    name="Guam",
    abbr="GU",
    capital="Hagåtña",
    capital_tz="Pacific/Guam",
    fips="66",
    url="https://guam.gov",
    unicameral=True,
    legislature_name="Guam Legislature",
    legislature_organization_id="ocd-organization/74999629-090b-4aa4-92ed-6eb86396017d",
    executive_name="Governor of Guam",
    executive_organization_id="ocd-organization/2ac004ab-9614-47a0-b9b4-58d5c90f8081",
    division_id="ocd-division/country:us/territory:gu",
    jurisdiction_id="ocd-jurisdiction/country:us/territory:gu/government",
    legislature=Chamber(
        chamber_type="unicameral",
        name="Guam Legislature",
        organization_id="ocd-organization/74999629-090b-4aa4-92ed-6eb86396017d",
        num_seats=15,
        title="Legislators",
        districts=simple_numbered_districts(
            "ocd-division/country:us/territory:gu", "legislature", 15
        ),
    ),
)
