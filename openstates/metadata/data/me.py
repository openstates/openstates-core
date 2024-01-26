from ..models import State, Chamber, District, simple_numbered_districts

ME = State(
    name="Maine",
    abbr="ME",
    capital="Augusta",
    capital_tz="America/New_York",
    fips="23",
    unicameral=False,
    legislature_name="Maine Legislature",
    legislature_organization_id="ocd-organization/1381ca6d-dedf-4bd3-8755-6f846f9e4848",
    executive_name="Office of the Governor",
    executive_organization_id="ocd-organization/1cb3f814-aad2-4343-8556-a2eb92f46230",
    division_id="ocd-division/country:us/state:me",
    jurisdiction_id="ocd-jurisdiction/country:us/state:me/government",
    url="http://legislature.maine.gov",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        organization_id="ocd-organization/a26314f0-dc6f-4cfc-99ca-dee4bafc9d4c",
        num_seats=152,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:me", "lower", 151
        ) + [District("Passamaquoddy Tribe", "lower",
                      "ocd-division/country:us/state:me/sldl:passamaquoddy-tribe")],
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        organization_id="ocd-organization/fe33521e-3c48-445a-adf7-75ff8a7674e4",
        num_seats=35,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:me", "upper", 35
        ),
    ),
)
