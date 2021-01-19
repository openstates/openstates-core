from .ak import AK
from .al import AL
from .ar import AR
from .az import AZ
from .ca import CA
from .co import CO
from .ct import CT
from .dc import DC
from .de import DE
from .fl import FL
from .ga import GA
from .hi import HI
from .ia import IA
from .id import ID
from .il import IL
from .ind import IN
from .ks import KS
from .ky import KY
from .la import LA
from .ma import MA
from .md import MD
from .me import ME
from .mi import MI
from .mn import MN
from .mo import MO
from .ms import MS
from .mt import MT
from .nc import NC
from .nd import ND
from .ne import NE
from .nh import NH
from .nj import NJ
from .nm import NM
from .nv import NV
from .ny import NY
from .oh import OH
from .ok import OK
from .ore import OR
from .pa import PA
from .pr import PR
from .ri import RI
from .sc import SC
from .sd import SD
from .tn import TN
from .tx import TX
from .us import US
from .ut import UT
from .va import VA
from .vt import VT
from .wa import WA
from .wi import WI
from .wv import WV
from .wy import WY


STATES = [
    AK,
    AL,
    AR,
    AZ,
    CA,
    CO,
    CT,
    DC,
    DE,
    FL,
    GA,
    HI,
    IA,
    ID,
    IL,
    IN,
    KS,
    KY,
    LA,
    MA,
    MD,
    ME,
    MI,
    MN,
    MO,
    MS,
    MT,
    NC,
    ND,
    NE,
    NH,
    NJ,
    NM,
    NV,
    NY,
    OH,
    OK,
    OR,
    PA,
    PR,
    RI,
    SC,
    SD,
    TN,
    TX,
    US,
    UT,
    VA,
    VT,
    WA,
    WI,
    WV,
    WY,
]

STATES_BY_ABBR = {s.abbr: s for s in STATES}
STATES_BY_JID = {s.jurisdiction_id: s for s in STATES}
STATES_BY_NAME = {s.name.lower(): s for s in STATES}
