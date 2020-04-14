from ..models import State, Chamber, simple_numbered_districts

AL = State(
    name="Alabama",
    abbr="AL",
    capital="Montgomery",
    capital_tz="America/Chicago",
    fips="01",
    unicameral=False,
    legislature_name="Alabama Legislature",
    legislature_organization_id="ocd-organization/8de9200f-a2e2-4f92-9950-e6c63f265248",
    executive_name="Office of the Governor",
    executive_organization_id="ocd-organization/f36ec162-a87e-57ab-976b-98b047a854f4",
    division_id="ocd-division/country:us/state:al",
    jurisdiction_id="ocd-jurisdiction/country:us/state:al/government",
    url="http://www.legislature.state.al.us/",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        organization_id="ocd-organization/74ad748b-f0a1-408f-9aa6-3319a868fd55",
        num_seats=105,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:al", "lower", 105
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        organization_id="ocd-organization/ddf820b5-5246-46b3-a807-99b5914ad39f",
        num_seats=35,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:al", "upper", 35
        ),
    ),
)
