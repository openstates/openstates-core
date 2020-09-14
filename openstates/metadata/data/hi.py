from ..models import State, Chamber, simple_numbered_districts

HI = State(
    name="Hawaii",
    abbr="HI",
    capital="Honolulu",
    capital_tz="Pacific/Honolulu",
    fips="15",
    unicameral=False,
    legislature_name="Hawaii State Legislature",
    legislature_organization_id="ocd-organization/c0ac26ed-60ea-42b7-bd02-20213257dbc5",
    executive_name="Office of the Governor",
    executive_organization_id="ocd-organization/8403b42b-dda0-5327-9ae1-599680374cc8",
    division_id="ocd-division/country:us/state:hi",
    jurisdiction_id="ocd-jurisdiction/country:us/state:hi/government",
    url="http://capitol.hawaii.gov",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        organization_id="ocd-organization/52cba4e0-aaeb-4d15-944b-089d559e97b6",
        num_seats=51,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:hi", "lower", 51
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        organization_id="ocd-organization/73058dca-37f9-4907-ac94-1f4ffd680586",
        num_seats=25,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:hi", "upper", 25
        ),
    ),
)
