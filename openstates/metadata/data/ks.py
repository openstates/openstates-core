from ..models import State, Chamber, simple_numbered_districts

KS = State(
    name="Kansas",
    abbr="KS",
    capital="Topeka",
    capital_tz="America/Chicago",
    fips="20",
    unicameral=False,
    legislature_name="Kansas State Legislature",
    legislature_organization_id="ocd-organization/6ee5506b-e33f-45c3-965e-59a531f249e6",
    executive_name="Office of the Governor",
    executive_organization_id="ocd-organization/433be248-0fd6-54cd-883b-2a1ab5f8b45d",
    division_id="ocd-division/country:us/state:ks",
    jurisdiction_id="ocd-jurisdiction/country:us/state:ks/government",
    url="http://www.kslegislature.org/",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        organization_id="ocd-organization/31d2e44e-f94c-4971-83ea-e1fe29613c73",
        num_seats=125,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:ks", "lower", 125
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        organization_id="ocd-organization/c1d465f9-fab5-4cc0-aded-270423bf31ba",
        num_seats=40,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:ks", "upper", 40
        ),
    ),
)
