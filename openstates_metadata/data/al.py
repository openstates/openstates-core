from ..models import State, Chamber, simple_numbered_districts

AL = State(
    name="Alabama",
    abbr="AL",
    capital="Montgomery",
    capital_tz="America/Chicago",
    fips="01",
    unicameral=False,
    legislature_name="Alabama Legislature",
    division_id="ocd-division/country:us/state:al",
    jurisdiction_id="ocd-jurisdiction/country:us/state:al/government",
    url="http://www.legislature.state.al.us/",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=105,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:al", "lower", 105
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=35,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:al", "upper", 35
        ),
    ),
)
