from .common import sources, extras, fuzzy_datetime_blank
from ...data import common


schema = {
    "type": "object",
    "properties": {
        "identifier": {"type": "string"},
        "motion_text": {"type": "string", "minLength": 1},
        "motion_classification": {
            "items": {"type": "string", "enum": common.VOTE_CLASSIFICATIONS},
            "type": "array",
        },
        "start_date": fuzzy_datetime_blank,
        "end_date": fuzzy_datetime_blank,
        "result": {"type": "string", "enum": common.VOTE_RESULTS},
        "organization": {"type": ["string", "null"], "minLength": 1},
        "legislative_session": {"type": "string", "minLength": 1},
        "bill": {"type": ["string", "null"], "minLength": 1},
        "bill_action": {"type": ["string", "null"], "minLength": 1},
        "bill_identifier": {"type": "string"},
        "votes": {
            "items": {
                "type": "object",
                "properties": {
                    "option": {"type": "string", "enum": common.VOTE_OPTIONS},
                    "voter_name": {"type": "string", "minLength": 1},
                    "voter_id": {"type": "string", "minLength": 1},
                    "note": {"type": "string"},
                },
            }
        },
        "counts": {
            "items": {
                "properties": {
                    "option": {"type": "string", "enum": common.VOTE_OPTIONS},
                    "value": {"type": "integer", "minimum": 0},
                },
                "type": "object",
            }
        },
        "sources": sources,
        "extras": extras,
        "dedupe_key": {"type": ["string", "null"], "minLength": 1},
    },
}
