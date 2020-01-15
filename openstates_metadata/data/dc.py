from ..models import State, Chamber, District

DC = State(
    name="District of Columbia",
    abbr="DC",
    capital="None",
    capital_tz="America/New_York",
    fips="11",
    unicameral=True,
    legislature_name="Council of the District of Columbia",
    division_id="ocd-division/country:us/district:dc",
    jurisdiction_id="ocd-jurisdiction/country:us/district:dc/government",
    url="https://dc.gov",
    legislature=Chamber(
        chamber_type="unicameral",
        name="Council of the District of Columbia",
        num_seats=13,
        title="Councilmember",
        districts=[
            District(
                "Ward 1", "legislature", 1, "ocd-division/country:us/district:dc/ward:1"
            ),
            District(
                "Ward 2", "legislature", 1, "ocd-division/country:us/district:dc/ward:2"
            ),
            District(
                "Ward 3", "legislature", 1, "ocd-division/country:us/district:dc/ward:3"
            ),
            District(
                "Ward 4", "legislature", 1, "ocd-division/country:us/district:dc/ward:4"
            ),
            District(
                "Ward 5", "legislature", 1, "ocd-division/country:us/district:dc/ward:5"
            ),
            District(
                "Ward 6", "legislature", 1, "ocd-division/country:us/district:dc/ward:6"
            ),
            District(
                "Ward 7", "legislature", 1, "ocd-division/country:us/district:dc/ward:7"
            ),
            District(
                "Ward 8", "legislature", 1, "ocd-division/country:us/district:dc/ward:8"
            ),
            District(
                "Chairman", "legislature", 1, "ocd-division/country:us/district:dc"
            ),
            District(
                "At-Large", "legislature", 4, "ocd-division/country:us/district:dc"
            ),
        ],
    ),
)
