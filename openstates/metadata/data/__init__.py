from .states import STATES
from .us import US

STATES_BY_ABBR = {s.abbr: s for s in STATES + [US]}
STATES_BY_JID = {s.jurisdiction_id: s for s in STATES + [US]}
STATES_BY_NAME = {s.name.lower(): s for s in STATES + [US]}
