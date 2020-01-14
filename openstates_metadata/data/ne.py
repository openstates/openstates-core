from ..models import State, Chamber, simple_numbered_districts

NE = State(
    name="Nebraska",
    abbr="NE",
    capital="Lincoln",
    capital_tz="America/Chicago",
    fips="31",
    unicameral=True,
    legislature_name="Nebraska Legislature",
    legislature=Chamber(
        chamber_type="unicameral",
        name="Nebraska Legislature",
        num_seats=49,
        title="Senator",
        districts=simple_numbered_districts(49),
    ),
)
