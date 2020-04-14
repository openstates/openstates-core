from ..models import State, Chamber, simple_numbered_districts

NE = State(
    name="Nebraska",
    abbr="NE",
    capital="Lincoln",
    capital_tz="America/Chicago",
    fips="31",
    unicameral=True,
    legislature_name="Nebraska Legislature",
    legislature_organization_id="ocd-organization/a0563aa3-1ab5-4e1e-afd1-643aca03b3b8",
    executive_name="Office of the Governor",
    executive_organization_id="ocd-organization/4ba67f40-0330-4d5a-ac31-8a939768d90b",
    division_id="ocd-division/country:us/state:ne",
    jurisdiction_id="ocd-jurisdiction/country:us/state:ne/government",
    url="http://nebraskalegislature.gov/",
    legislature=Chamber(
        chamber_type="unicameral",
        name="Nebraska Legislature",
        organization_id="ocd-organization/a0563aa3-1ab5-4e1e-afd1-643aca03b3b8",
        num_seats=49,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:ne", "legislature", 49
        ),
    ),
)
