from ..models import State, Chamber, District

ZA = State(
    name="South Africa",
    abbr="ZA",
    capital="Cape Town",
    capital_tz="Africa/Johannesburg",
    fips="SF",
    unicameral=False,
    legislature_name="South Africa Parliament",
    legislature_organization_id="ocd-organization/de2b7383-ee98-4f01-bc99-650ba84358a4",
    executive_name="President of the South Africa",
    executive_organization_id="ocd-organization/2c4b6383-7560-4c15-8266-6fc6b717a8ef",
    division_id="ocd-division/country:za",
    jurisdiction_id="ocd-jurisdiction/country:za/government",
    url="https://www.parliament.gov.za/",
    lower=Chamber(
        chamber_type="lower",
        name="National Assembly",
        organization_id="ocd-organization/fac94935-991f-424f-b02a-8f1336a6e540",
        num_seats=400,
        title="Member",
        districts=[
            # made up ocd-divisions based on party abbreviations since there aren't official ones and the number of
            # seats are based on the number of voters that voted for each party in the elections
            # https://www.parliament.gov.za/national-assembly
            District(
                "African National Congress",
                "lower",
                "ocd-division/country:za/party:anc",
                230,
            ),
            District(
                "Democratic Alliance",
                "lower",
                "ocd-division/country:za/party:da",
                84,
            ),
            District(
                "Economic Freedom Fighters",
                "lower",
                "ocd-division/country:za/party:dff",
                44,
            ),
            District(
                "Inkatha Freedom Party",
                "lower",
                "ocd-division/country:za/party:ifp",
                14,
            ),
            District(
                "Freedom Front Plus",
                "lower",
                "ocd-division/country:za/party:ff-plus",
                10,
            ),
            District(
                "African Christian Democratic Party",
                "lower",
                "ocd-division/country:za/party:acdp",
                4,
            ),
            District(
                "United Democratic Movement",
                "lower",
                "ocd-division/country:za/party:udm",
                2,
            ),
            District(
                "African Transformation Movement",
                "lower",
                "ocd-division/country:za/party:atm",
                2,
            ),
            District(
                "Good Party",
                "lower",
                "ocd-division/country:za/party:good",
                2,
            ),
            District(
                "National Freedom Party",
                "lower",
                "ocd-division/country:za/party:ntp",
                2,
            ),
            District(
                "African Independent Congress",
                "lower",
                "ocd-division/country:za/party:aic",
                2,
            ),
            District(
                "Congress of the People",
                "lower",
                "ocd-division/country:za/party:cope",
                2,
            ),
            District(
                "Pan Africanist Congress",
                "lower",
                "ocd-division/country:za/party:pac",
                1,
            ),
            District(
                "Al Jama-ah",
                "lower",
                "ocd-division/country:za/party:aljama-ah",
                1,
            ),
        ],
    ),
    upper=Chamber(
        chamber_type="upper",
        name="National Council of Provinces",
        organization_id="ocd-organization/33ec4697-6a77-4edb-a279-1f8df6509469",
        num_seats=90,
        title="Member",
        districts=[
            # ocd-divisions found here
            # https://github.com/opencivicdata/ocd-division-ids/blob/master/identifiers/country-za/provinces.csv
            District(
                "Eastern Cape",
                "upper",
                "ocd-division/country:za/province:ec",
                10,
            ),
            District(
                "Free State",
                "upper",
                "ocd-division/country:za/province:fs",
                10,
            ),
            District(
                "Gauteng",
                "upper",
                "ocd-division/country:za/province:gp",
                10,
            ),
            District(
                "KwaZulu-Natal",
                "upper",
                "ocd-division/country:za/province:kzn",
                10,
            ),
            District(
                "Limpopo",
                "upper",
                "ocd-division/country:za/province:lp",
                10,
            ),
            District(
                "Mpumalanga",
                "upper",
                "ocd-division/country:za/province:mp",
                10,
            ),
            District(
                "Northern Cape",
                "upper",
                "ocd-division/country:za/province:nc",
                10,
            ),
            District(
                "North West",
                "upper",
                "ocd-division/country:za/province:nw",
                10,
            ),
            District(
                "Western Cape",
                "upper",
                "ocd-division/country:za/province:wc",
                10,
            ),
        ]
    ),
)
