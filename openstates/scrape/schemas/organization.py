from .common import (
    links,
    identifiers,
    other_names,
    sources,
    extras,
    fuzzy_datetime,
    jurisdiction_summary,
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
        "links": links,
        "sources": sources,
        # added to popolo
        "jurisdiction_id": {"type": "string", "minLength": 1},
        "division_id": {"type": ["string", "null"], "minLength": 1},
        "extras": extras,
        "jurisdiction": jurisdiction_summary,
        "scraped_at": fuzzy_datetime,
    },
    "type": "object",
}
