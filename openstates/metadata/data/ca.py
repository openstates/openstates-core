from ..models import State, Chamber, simple_numbered_districts

CA = State(
    name="California",
    abbr="CA",
    capital="Sacramento",
    capital_tz="America/Los_Angeles",
    fips="06",
    unicameral=False,
    legislature_name="California State Legislature",
    legislature_organization_id="ocd-organization/f1c6eb47-c439-42e5-9b6f-d7f6121f20e9",
    executive_name="Office of the Governor",
    executive_organization_id="ocd-organization/b7f8d62d-b8f0-4eba-8de3-a42c1f64f9fe",
    division_id="ocd-division/country:us/state:ca",
    jurisdiction_id="ocd-jurisdiction/country:us/state:ca/government",
    url="http://www.legislature.ca.gov/",
    lower=Chamber(
        chamber_type="lower",
        name="Assembly",
        organization_id="ocd-organization/e70e812e-44d2-46b0-9eae-2f3b9a1d5150",
        num_seats=80,
        title="Assemblymember",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:ca", "lower", 80
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        organization_id="ocd-organization/98623fa0-f9c3-47ae-80bb-51465349ed71",
        num_seats=40,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:ca", "upper", 40
        ),
    ),
)
