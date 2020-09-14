from .common import (
    links,
    contact_details,
    identifiers,
    other_names,
    sources,
    extras,
)
from ...data import common

schema = {
    "properties": {
        "name": {"type": "string", "minLength": 1},
        "other_names": other_names,
        "identifiers": identifiers,
        "classification": {
            "type": ["string", "null"],
            "enum": common.ORGANIZATION_CLASSIFICATIONS,
        },
        "parent_id": {"type": ["string", "null"]},
        "contact_details": contact_details,
        "links": links,
        "sources": sources,
        # added to popolo
        "jurisdiction_id": {"type": "string", "minLength": 1},
        "division_id": {"type": ["string", "null"], "minLength": 1},
        "extras": extras,
    },
    "type": "object",
}
