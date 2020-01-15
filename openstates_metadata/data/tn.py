from ..models import State, Chamber, simple_numbered_districts

TN = State(
    name="Tennessee",
    abbr="TN",
    capital="Nashville",
    capital_tz="America/Chicago",
    fips="47",
    unicameral=False,
    legislature_name="Tennessee General Assembly",
    division_id="ocd-division/country:us/state:tn",
    jurisdiction_id="ocd-jurisdiction/country:us/state:tn/government",
    url="http://www.capitol.tn.gov/",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=99,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:tn", "lower", 99
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=33,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:tn", "upper", 33
        ),
    ),
)
