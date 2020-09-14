from ..models import State, Chamber, District

DC = State(
    name="District of Columbia",
    abbr="DC",
    capital="None",
    capital_tz="America/New_York",
    fips="11",
    unicameral=True,
    legislature_name="Council of the District of Columbia",
    legislature_organization_id="ocd-organization/393504d5-b5ba-446f-908b-9868996bf3f7",
    executive_name="Office of the Governor",
    executive_organization_id="ocd-organization/86e53984-1898-47b4-b74b-b3de66455937",
    division_id="ocd-division/country:us/district:dc",
    jurisdiction_id="ocd-jurisdiction/country:us/district:dc/government",
    url="https://dc.gov",
    legislature=Chamber(
        chamber_type="unicameral",
        name="Council of the District of Columbia",
        organization_id="ocd-organization/393504d5-b5ba-446f-908b-9868996bf3f7",
        num_seats=13,
        title="Councilmember",
        districts=[
            District(
                "Ward 1", "legislature", "ocd-division/country:us/district:dc/ward:1", 1
            ),
            District(
                "Ward 2", "legislature", "ocd-division/country:us/district:dc/ward:2", 1
            ),
            District(
                "Ward 3", "legislature", "ocd-division/country:us/district:dc/ward:3", 1
            ),
            District(
                "Ward 4", "legislature", "ocd-division/country:us/district:dc/ward:4", 1
            ),
            District(
                "Ward 5", "legislature", "ocd-division/country:us/district:dc/ward:5", 1
            ),
            District(
                "Ward 6", "legislature", "ocd-division/country:us/district:dc/ward:6", 1
            ),
            District(
                "Ward 7", "legislature", "ocd-division/country:us/district:dc/ward:7", 1
            ),
            District(
                "Ward 8", "legislature", "ocd-division/country:us/district:dc/ward:8", 1
            ),
            District(
                "Chairman", "legislature", "ocd-division/country:us/district:dc", 1
            ),
            District(
                "At-Large", "legislature", "ocd-division/country:us/district:dc", 4
            ),
        ],
    ),
)
