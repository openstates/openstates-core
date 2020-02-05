from .data import STATES_BY_ABBR, STATES_BY_JID, STATES_BY_NAME


def lookup(*, abbr=None, jurisdiction_id=None, name=None):
    if abbr:
        return STATES_BY_ABBR[abbr.upper()]
    if name:
        return STATES_BY_NAME[name.lower()]
    if jurisdiction_id:
        return STATES_BY_JID[jurisdiction_id]
