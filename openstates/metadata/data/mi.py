from ..models import State, Chamber, simple_numbered_districts

MI = State(
    name="Michigan",
    abbr="MI",
    capital="Lansing",
    capital_tz="America/New_York",
    fips="26",
    unicameral=False,
    legislature_name="Michigan Legislature",
    legislature_organization_id="ocd-organization/c70eb47a-43c1-4aa1-95a6-2aea30da8e82",
    executive_name="Office of the Governor",
    executive_organization_id="ocd-organization/1435164b-be3c-56fd-b426-678565c853cd",
    division_id="ocd-division/country:us/state:mi",
    jurisdiction_id="ocd-jurisdiction/country:us/state:mi/government",
    url="http://www.legislature.mi.gov",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        organization_id="ocd-organization/d387cf69-631c-4013-bb32-4a00c848fcc4",
        num_seats=110,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:mi", "lower", 110
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        organization_id="ocd-organization/7cf9891c-6c1f-45ec-b24c-7aa9be45e9cc",
        num_seats=38,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:mi", "upper", 38
        ),
    ),
)
