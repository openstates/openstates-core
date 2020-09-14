from ..models import State, Chamber, simple_numbered_districts

NY = State(
    name="New York",
    abbr="NY",
    capital="Albany",
    capital_tz="America/New_York",
    fips="36",
    unicameral=False,
    legislature_name="New York Legislature",
    legislature_organization_id="ocd-organization/700d3e60-3b1a-4cba-9aa4-06278aa7605d",
    executive_name="Office of the Governor",
    executive_organization_id="ocd-organization/4074536a-6e18-56f0-b004-3e85742b0c98",
    division_id="ocd-division/country:us/state:ny",
    jurisdiction_id="ocd-jurisdiction/country:us/state:ny/government",
    url="http://public.leginfo.state.ny.us/",
    lower=Chamber(
        chamber_type="lower",
        name="Assembly",
        organization_id="ocd-organization/26bb6306-85f0-4d10-bff7-d1cd5bdc0865",
        num_seats=150,
        title="Assembly Member",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:ny", "lower", 150
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        organization_id="ocd-organization/8291a233-623d-40e8-882d-21ec2d382c87",
        num_seats=63,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:ny", "upper", 63
        ),
    ),
)
