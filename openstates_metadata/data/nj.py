from ..models import State, Chamber, simple_numbered_districts

NJ = State(
    name="New Jersey",
    abbr="NJ",
    capital="Trenton",
    capital_tz="America/New_York",
    fips="34",
    unicameral=False,
    legislature_name="New jersey Legislature",
    division_id="ocd-division/country:us/state:nj",
    jurisdiction_id="ocd-jurisdiction/country:us/state:nj/government",
    url="http://www.njleg.state.nj.us/",
    lower=Chamber(
        chamber_type="lower",
        name="Assembly",
        num_seats=80,
        title="Assembly Member",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:nj", "lower", 40, num_seats=2
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=40,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:nj", "upper", 40
        ),
    ),
)
