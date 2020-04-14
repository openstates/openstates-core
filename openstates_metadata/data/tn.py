from ..models import State, Chamber, simple_numbered_districts

TN = State(
    name="Tennessee",
    abbr="TN",
    capital="Nashville",
    capital_tz="America/Chicago",
    fips="47",
    unicameral=False,
    legislature_name="Tennessee General Assembly",
    legislature_organization_id="ocd-organization/2010a137-d178-48fe-a66e-692e97a12fcf",
    executive_name="Office of the Governor",
    executive_organization_id="ocd-organization/81395620-423b-599c-b77c-a0714bff3357",
    division_id="ocd-division/country:us/state:tn",
    jurisdiction_id="ocd-jurisdiction/country:us/state:tn/government",
    url="http://www.capitol.tn.gov/",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        organization_id="ocd-organization/47760e16-8071-49dd-bd9f-354198c8b653",
        num_seats=99,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:tn", "lower", 99
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        organization_id="ocd-organization/d4c442c8-d4d7-4ea9-a3fd-b856b2904d8b",
        num_seats=33,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:tn", "upper", 33
        ),
    ),
)
