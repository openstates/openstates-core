from ..models import State, Chamber, simple_numbered_districts

UT = State(
    name="Utah",
    abbr="UT",
    capital="Salt Lake City",
    capital_tz="America/Denver",
    fips="49",
    unicameral=False,
    legislature_name="Utah State Legislature",
    division_id="ocd-division/country:us/state:ut",
    jurisdiction_id="ocd-jurisdiction/country:us/state:ut/government",
    url="http://le.utah.gov/",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        organization_id="ocd-organization/c7625e7e-dc12-49cf-aa73-fa96c5bf4b11",
        num_seats=75,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:ut", "lower", 75
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        organization_id="ocd-organization/98cb21d7-f3ae-416b-93e7-df3da962aff9",
        num_seats=29,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:ut", "upper", 29
        ),
    ),
)
