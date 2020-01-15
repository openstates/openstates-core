from ..models import State, Chamber, simple_numbered_districts

NY = State(
    name="New York",
    abbr="NY",
    capital="Albany",
    capital_tz="America/New_York",
    fips="36",
    unicameral=False,
    legislature_name="New York Legislature",
    division_id="ocd-division/country:us/state:ny",
    jurisdiction_id="ocd-jurisdiction/country:us/state:ny/government",
    url="http://public.leginfo.state.ny.us/",
    lower=Chamber(
        chamber_type="lower",
        name="Assembly",
        num_seats=150,
        title="Assembly Member",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:ny", "lower", 150
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=63,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:ny", "upper", 63
        ),
    ),
)
