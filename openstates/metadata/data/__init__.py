from . import states
from .us import US

STATES = states.STATES

STATES_BY_ABBR = {s.abbr: s for s in STATES + [US]}
STATES_BY_JID = {s.jurisdiction_id: s for s in STATES + [US]}
STATES_BY_NAME = {s.name.lower(): s for s in STATES + [US]}
