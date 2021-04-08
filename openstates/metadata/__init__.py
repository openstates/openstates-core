import typing
from .data import STATES_BY_ABBR, STATES_BY_JID, STATES_BY_NAME
from .models import State, Chamber, District


def lookup(
    *,
    abbr: typing.Optional[str] = None,
    jurisdiction_id: typing.Optional[str] = None,
    name: typing.Optional[str] = None,
) -> State:
    if abbr:
        return STATES_BY_ABBR[abbr.upper()]
    if name:
        return STATES_BY_NAME[name.lower()]
    if jurisdiction_id:
        return STATES_BY_JID[jurisdiction_id]
    raise ValueError(f"invalid lookup call {abbr} {jurisdiction_id} {name}")


def lookup_district_with_ancestors(
    *, division_id: str
) -> typing.Tuple[State, Chamber, District]:
    district: typing.Optional[District] = None
    pieces = division_id.split("/")
    if len(pieces) == 4:
        state_portion = pieces[2]
    elif len(pieces) == 3:
        # special case the at-large ids for now, these should be fixed
        if division_id == "ocd-division/country:us/territory:pr":
            state = typing.cast(State, lookup(abbr="pr"))
            chamber = typing.cast(Chamber, state.upper)
        elif division_id == "ocd-division/country:us/district:dc":
            state = typing.cast(State, lookup(abbr="dc"))
            chamber = typing.cast(Chamber, state.legislature)
        district = typing.cast(District, chamber.lookup_district(name="At-Large"))
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
        chamber = typing.cast(Chamber, state.legislature)
    elif "sldl" in division_id:
        chamber = typing.cast(Chamber, state.lower)
    elif "sldu" in division_id:
        chamber = typing.cast(Chamber, state.upper)

    return state, chamber, district
