from . import states
from .us import US

STATES = states.STATES
TERRITORIES = states.TERRITORIES
STATES_AND_TERRITORIES = STATES + TERRITORIES

STATES_BY_ABBR = {s.abbr: s for s in STATES_AND_TERRITORIES + [US]}
STATES_BY_JID = {s.jurisdiction_id: s for s in STATES_AND_TERRITORIES + [US]}
STATES_BY_NAME = {s.name.lower(): s for s in STATES_AND_TERRITORIES + [US]}
