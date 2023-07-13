from . import states
from .pr import PR
from .dc import DC
from .us import US
from .za import ZA

STATES = states.STATES
TERRITORIES = states.TERRITORIES
STATES_AND_TERRITORIES = STATES + TERRITORIES + states.DISTRICTS
STATES_AND_DC_PR = STATES + [DC, PR]

STATES_BY_ABBR = {s.abbr: s for s in STATES_AND_TERRITORIES + [US, ZA]}
STATES_BY_JID = {s.jurisdiction_id: s for s in STATES_AND_TERRITORIES + [US, ZA]}
STATES_BY_NAME = {s.name.lower(): s for s in STATES_AND_TERRITORIES + [US, ZA]}
