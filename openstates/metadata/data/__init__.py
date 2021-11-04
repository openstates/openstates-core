from . import states
from .dc import DC
from .pr import PR
from .us import US

STATES = states.STATES
STATES_AND_DC_PR = STATES + [DC, PR]

STATES_BY_ABBR = {s.abbr: s for s in STATES_AND_DC_PR + [US]}
STATES_BY_JID = {s.jurisdiction_id: s for s in STATES_AND_DC_PR + [US]}
STATES_BY_NAME = {s.name.lower(): s for s in STATES_AND_DC_PR + [US]}
