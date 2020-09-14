from ..models import State, Chamber, simple_numbered_districts

NC = State(
    name="North Carolina",
    abbr="NC",
    capital="Raleigh",
    capital_tz="America/New_York",
    fips="37",
    unicameral=False,
    legislature_name="North Carolina General Assembly",
    legislature_organization_id="ocd-organization/32aab083-d7a0-44e0-9b95-a7790c542605",
    executive_name="Office of the Governor",
    executive_organization_id="ocd-organization/097fcec3-4290-42eb-927f-0a786b873093",
    division_id="ocd-division/country:us/state:nc",
    jurisdiction_id="ocd-jurisdiction/country:us/state:nc/government",
    url="http://www.ncleg.net/",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        organization_id="ocd-organization/4861d484-9f30-411a-baaf-c2c12d4d174f",
        num_seats=120,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:nc", "lower", 120
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        organization_id="ocd-organization/6347dffa-4778-4dc0-97d7-fd4db3ff5328",
        num_seats=50,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:nc", "upper", 50
        ),
    ),
)
