from .data import STATES_BY_ABBR, STATES_BY_JID


def lookup(*, abbr=None, jurisdiction_id=None):
    if abbr:
        return STATES_BY_ABBR[abbr.upper()]
    if jurisdiction_id:
        return STATES_BY_JID[jurisdiction_id]
