from ..models import State, Chamber, simple_numbered_districts

PA = State(
    name="Pennsylvania",
    abbr="PA",
    capital="Harrisburg",
    capital_tz="America/New_York",
    fips="42",
    unicameral=False,
    legislature_name="Pennsylvania General Assembly",
    division_id="ocd-division/country:us/state:pa",
    jurisdiction_id="ocd-jurisdiction/country:us/state:pa/government",
    url="http://www.legis.state.pa.us/",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=203,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:pa", "lower", 203
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=50,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:pa", "upper", 50
        ),
    ),
)
