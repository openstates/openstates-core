from ..models import State, Chamber, simple_numbered_districts

US = State(
    name="United States",
    abbr="US",
    capital="Washington DC",
    capital_tz="America/New_York",
    fips="00",
    unicameral=False,
    legislature_name="US Congress",
    legislature_organization_id="ocd-organization/98590d80-8f8a-57fa-bdfc-55d778fbd88a",
    executive_name="Office of the Governor",
    executive_organization_id="ocd-organization/072da2ce-df81-52c3-9cc8-323e208cdf10",
    division_id="ocd-division/country:us/state:us",
    jurisdiction_id="ocd-jurisdiction/country:us/state:us/government",
    url="http://congress.gov",
    
                lower=Chamber(chamber_type="lower", name="House", organization_id="ocd-organization/24af4233-d9b5-5933-91b2-51d29f721037",
                   num_seats=435, title="Representative", districts=simple_numbered_districts('ocd-division/country:us/state:us', 'lower', 435)),
                upper=Chamber(chamber_type="upper", name="Senate", organization_id="ocd-organization/c187ea65-5cd6-42fb-b08b-18e487855526",
                   num_seats=100, title="Senator", districts=simple_numbered_districts('ocd-division/country:us/state:us', 'upper', 100),),
        
)