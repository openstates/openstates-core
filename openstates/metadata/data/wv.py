from ..models import State, Chamber, simple_numbered_districts

WV = State(
    name="West Virginia",
    abbr="WV",
    capital="Charleston",
    capital_tz="America/New_York",
    fips="54",
    unicameral=False,
    legislature_name="West Virginia Legislature",
    legislature_organization_id="ocd-organization/237dc1a5-2314-433e-887e-d63a970cf67d",
    executive_name="Office of the Governor",
    executive_organization_id="ocd-organization/193c7d7d-3161-5a34-a7b1-df72b553b7f3",
    division_id="ocd-division/country:us/state:wv",
    jurisdiction_id="ocd-jurisdiction/country:us/state:wv/government",
    url="http://www.legis.state.wv.us/",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        organization_id="ocd-organization/3fcd7789-fa25-4d8b-a4b9-7c0d1d0f8bc4",
        num_seats=100,
        title="Delegate",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:wv", "lower", 100
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        organization_id="ocd-organization/660bc141-f4cb-4d98-b334-b12b637776ba",
        num_seats=34,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:wv",
            "upper",
            17,
            num_seats=2,
        ),
    ),
)
