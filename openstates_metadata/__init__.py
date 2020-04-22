from .data import STATES_BY_ABBR, STATES_BY_JID, STATES_BY_NAME


def lookup(*, abbr=None, jurisdiction_id=None, name=None):
    if abbr:
        return STATES_BY_ABBR[abbr.upper()]
    if name:
        return STATES_BY_NAME[name.lower()]
    if jurisdiction_id:
        return STATES_BY_JID[jurisdiction_id]


def lookup_district_with_ancestors(*, division_id):
    try:
        _, _, state_portion, _ = division_id.split("/")
    except ValueError:
        raise ValueError(f"invalid division id: {division_id}")

    try:
        state = lookup(abbr=state_portion.split(":")[1])
    except KeyError:
        raise ValueError(f"invalid division id: {division_id}")

    district = state.lookup_district(division_id)

    if not district:
        raise ValueError(f"invalid division id: {division_id}")

    if state.unicameral:
        chamber = state.legislature
    elif "sldl" in division_id:
        chamber = state.lower
    elif "sldu" in division_id:
        chamber = state.upper

    return state, chamber, district
