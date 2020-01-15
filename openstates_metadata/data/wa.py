from ..models import State, Chamber, simple_numbered_districts

WA = State(
    name="Washington",
    abbr="WA",
    capital="Olympia",
    capital_tz="America/Los_Angeles",
    fips="53",
    unicameral=False,
    legislature_name="Washington State Legislature",
    division_id="ocd-division/country:us/state:wa",
    jurisdiction_id="ocd-jurisdiction/country:us/state:wa/government",
    url="http://www.leg.wa.gov",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=98,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:wa", "lower", 49, num_seats=2
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=49,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:wa", "upper", 49
        ),
    ),
)
