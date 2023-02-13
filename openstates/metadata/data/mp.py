from ..models import State

AS = State(
    name="Northern Mariana Islands",
    abbr="MP",
    capital="Saipan",
    capital_tz="Pacific/Guam",
    fips="69",
    unicameral=False,
    # 2023-02-13 -> site is a default nginx page
    url="https://gov.mp",
    legislature_name="Northern Marianas Commonwealth Legislature",
    # legislature_organization_id="ocd-organization/803c558f-dec2-4f43-9c35-e73a6e849408",
    executive_name="Office of Governor",
    # executive_organization_id="ocd-organization/2838c5e6-e793-518d-a722-6140d5f8d0aa",
    division_id="ocd-division/country:us/territory:mp",
    jurisdiction_id="ocd-jurisdiction/country:us/territory:mp/government",
)
