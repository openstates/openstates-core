from ..models import State, Chamber, simple_numbered_districts

SC = State(
    name="South Carolina",
    abbr="SC",
    capital="Columbia",
    capital_tz="America/New_York",
    fips="45",
    unicameral=False,
    legislature_name="South Carolina Legislature",
    division_id="ocd-division/country:us/state:sc",
    jurisdiction_id="ocd-jurisdiction/country:us/state:sc/government",
    url="http://www.scstatehouse.gov/",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=124,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:sc", "lower", 124
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=46,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:sc", "upper", 46
        ),
    ),
)
