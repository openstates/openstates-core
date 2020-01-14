from ..models import State, Chamber, District

DC = State(
    name="District of Columbia",
    abbr="DC",
    capital="None",
    capital_tz="America/New_York",
    fips="11",
    unicameral=True,
    legislature_name="Council of the District of Columbia",
    legislature=Chamber(
        chamber_type="unicameral",
        name="Council of the District of Columbia",
        num_seats=13,
        title="Councilmember",
        districts=[
            District("Ward 1", 1, "ocd-division/country:us/district:dc/ward:1"),
            District("Ward 2", 1, "ocd-division/country:us/district:dc/ward:2"),
            District("Ward 3", 1, "ocd-division/country:us/district:dc/ward:3"),
            District("Ward 4", 1, "ocd-division/country:us/district:dc/ward:4"),
            District("Ward 5", 1, "ocd-division/country:us/district:dc/ward:5"),
            District("Ward 6", 1, "ocd-division/country:us/district:dc/ward:6"),
            District("Ward 7", 1, "ocd-division/country:us/district:dc/ward:7"),
            District("Ward 8", 1, "ocd-division/country:us/district:dc/ward:8"),
            District("Chairman", 1, "ocd-division/country:us/district:dc"),
            District("At-Large", 4, "ocd-division/country:us/district:dc"),
        ],
    ),
)
