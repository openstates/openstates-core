from ..models import State, Chamber, simple_numbered_districts

HI = State(
    name="Hawaii",
    abbr="HI",
    capital="Honolulu",
    capital_tz="Pacific/Honolulu",
    fips="15",
    unicameral=False,
    legislature_name="Hawaii State Legislature",
    division_id="ocd-division/country:us/state:hi",
    jurisdiction_id="ocd-jurisdiction/country:us/state:hi/government",
    url="http://capitol.hawaii.gov",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=51,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:hi", "lower", 51
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=25,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:hi", "upper", 25
        ),
    ),
)
