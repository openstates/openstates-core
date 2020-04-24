from .data import STATES_BY_ABBR, STATES_BY_JID, STATES_BY_NAME


def lookup(*, abbr=None, jurisdiction_id=None, name=None):
    if abbr:
        return STATES_BY_ABBR[abbr.upper()]
    if name:
        return STATES_BY_NAME[name.lower()]
    if jurisdiction_id:
        return STATES_BY_JID[jurisdiction_id]


def lookup_district_with_ancestors(*, division_id):
    pieces = division_id.split("/")
    if len(pieces) == 4:
        state_portion = pieces[2]
    elif len(pieces) == 3:
        # special case the at-large ids for now, these should be fixed
        if division_id == "ocd-division/country:us/territory:pr":
            state = lookup(abbr="pr")
            chamber = state.upper
        elif division_id == "ocd-division/country:us/district:dc":
            state = lookup(abbr="dc")
            chamber = state.legislature
        district = chamber.lookup_district(name="At-Large")
        return state, chamber, district
    else:
        raise ValueError(f"invalid division id: {division_id}")

    try:
        state = lookup(abbr=state_portion.split(":")[1])
    except KeyError:
        raise ValueError(f"invalid division id: {division_id}, no such state")

    district = state.lookup_district(division_id)

    if not district:
        raise ValueError(f"invalid division id: {division_id}, no such district")

    if state.unicameral:
        chamber = state.legislature
    elif "sldl" in division_id:
        chamber = state.lower
    elif "sldu" in division_id:
        chamber = state.upper

    return state, chamber, district
