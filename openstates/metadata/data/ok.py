from ..models import State, Chamber, simple_numbered_districts

OK = State(
    name="Oklahoma",
    abbr="OK",
    capital="Oklahoma City",
    capital_tz="America/Chicago",
    fips="40",
    unicameral=False,
    legislature_name="Oklahoma Legislature",
    legislature_organization_id="ocd-organization/a720b7e9-ab67-405a-a209-473e9d6a6036",
    executive_name="Office of the Governor",
    executive_organization_id="ocd-organization/804e97df-c92a-577e-b610-545671bf7ed1",
    division_id="ocd-division/country:us/state:ok",
    jurisdiction_id="ocd-jurisdiction/country:us/state:ok/government",
    url="http://www.oklegislature.gov/",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        organization_id="ocd-organization/cba1f18c-65a2-4eb0-886d-eada16da3d8a",
        num_seats=101,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:ok", "lower", 101
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        organization_id="ocd-organization/5c78775c-6ff3-4cf8-a5f2-4e5e550861f3",
        num_seats=48,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:ok", "upper", 48
        ),
    ),
)
