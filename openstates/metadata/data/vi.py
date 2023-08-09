from ..models import State, Chamber, simple_numbered_districts

VI = State(
    name="Virgin Islands",
    abbr="VI",
    capital="Charlotte Amalie",
    capital_tz="America/Puerto_Rico",
    fips="78",
    url="https://legvi.org",
    unicameral=True,
    legislature_name="Legislature of the Virgin Islands",
    legislature_organization_id="ocd-organization/7caa0f66-1197-46d4-82e6-6a98129b0a96",
    executive_name="Office of the Governor",
    executive_organization_id="ocd-organization/20779ed0-c5f5-4c90-8c06-d972aed7b4b7",
    division_id="ocd-division/country:us/territory:vi",
    jurisdiction_id="ocd-jurisdiction/country:us/territory:vi/government",
    legislature=Chamber(
        chamber_type="unicameral",
        name="Legislature",
        organization_id="ocd-organization/7caa0f66-1197-46d4-82e6-6a98129b0a96",
        num_seats=15,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/territory:vi", "legislature", 15
        ),
    ),
)
