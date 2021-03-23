from ..models import State, Chamber, District
from us import STATES


seats_by_state = {
    "AL": 7,
    "AK": 1,
    "AZ": 9,
    "AR": 4,
    "CA": 53,
    "CO": 7,
    "CT": 5,
    "DE": 1,
    "FL": 27,
    "GA": 14,
    "HI": 2,
    "ID": 2,
    "IL": 18,
    "IN": 9,
    "IA": 4,
    "KS": 4,
    "KY": 6,
    "LA": 6,
    "ME": 2,
    "MD": 8,
    "MA": 9,
    "MI": 14,
    "MN": 8,
    "MS": 4,
    "MO": 8,
    "MT": 1,
    "NE": 3,
    "NV": 4,
    "NH": 2,
    "NJ": 12,
    "NM": 3,
    "NY": 27,
    "NC": 13,
    "ND": 1,
    "OH": 16,
    "OK": 5,
    "OR": 5,
    "PA": 18,
    "RI": 2,
    "SC": 7,
    "SD": 1,
    "TN": 9,
    "TX": 36,
    "UT": 4,
    "VT": 1,
    "VA": 11,
    "WA": 10,
    "WV": 3,
    "WI": 8,
    "WY": 1,
}


def us_house_districts():
    districts = []

    # TODO: add other territories
    territories = [
        District(
            "DC-AL",
            "lower",
            "ocd-division/country:us/district:dc",
            title_override="Delegate",
        ),
        District(
            "PR-AL",
            "lower",
            "ocd-division/country:us/territory:pr",
            title_override="Resident Commissioner",
        ),
    ]
    districts += territories

    for abbr, num_districts in seats_by_state.items():
        if num_districts == 1:
            districts.append(
                District(
                    abbr + "-AL",
                    "lower",
                    f"ocd-division/country:us/state:{abbr.lower()}/cd:at-large",
                )
            )
        else:
            districts.extend(
                [
                    District(
                        f"{abbr}-{n}",
                        "lower",
                        f"ocd-division/country:us/state:{abbr.lower()}/cd:{n}",
                    )
                    for n in range(1, num_districts + 1)
                ]
            )
    return districts


def us_senate_districts():
    return [
        District(s.name, "upper", f"ocd-division/country:us/state:{s.abbr.lower()}", 2)
        for s in STATES
    ]


US = State(
    name="United States",
    abbr="US",
    capital="Washington DC",
    capital_tz="America/New_York",
    fips="00",
    unicameral=False,
    legislature_name="US Congress",
    legislature_organization_id="ocd-organization/98590d80-8f8a-57fa-bdfc-55d778fbd88a",
    executive_name="President of the United States",
    executive_organization_id="ocd-organization/16b52117-31a3-5f05-96a6-fd580a4f9f4d",
    division_id="ocd-division/country:us",
    jurisdiction_id="ocd-jurisdiction/country:us/government",
    url="https://usa.gov",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        organization_id="ocd-organization/24af4233-d9b5-5933-91b2-51d29f721037",
        num_seats=437,
        title="Representative",
        districts=us_house_districts(),
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        organization_id="ocd-organization/072da2ce-df81-52c3-9cc8-323e208cdf10",
        num_seats=100,
        title="Senator",
        districts=us_senate_districts(),
    ),
)
