from ..models import State, Chamber, simple_numbered_districts

SC = State(
    name="South Carolina",
    abbr="SC",
    capital="Columbia",
    capital_tz="America/New_York",
    fips="45",
    unicameral=False,
    legislature_name="South Carolina Legislature",
    legislature_organization_id="ocd-organization/57920b9f-163e-4cc3-9642-e616579b47ee",
    executive_name="Office of the Governor",
    executive_organization_id="ocd-organization/852b2773-ace9-5d16-b69b-ecc11f74b548",
    division_id="ocd-division/country:us/state:sc",
    jurisdiction_id="ocd-jurisdiction/country:us/state:sc/government",
    url="http://www.scstatehouse.gov/",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        organization_id="ocd-organization/11144d16-6b61-4e2a-94fe-6f9c24e36193",
        num_seats=124,
        title="Representative",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:sc", "lower", 124
        ),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        organization_id="ocd-organization/705ec497-4b18-4a39-a0e0-ce114a2f3c78",
        num_seats=46,
        title="Senator",
        districts=simple_numbered_districts(
            "ocd-division/country:us/state:sc", "upper", 46
        ),
    ),
)
