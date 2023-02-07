import copy
from .common import extras, fuzzy_date

required_date = copy.deepcopy(fuzzy_date)
required_date["required"] = True

schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "minLength": 1},
        "url": {"type": "string", "minLength": 1},
        "classification": {"type": "string", "minLength": 1},  # TODO: enum
        "division_id": {"type": "string", "minLength": 1},
        "legislative_sessions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "minLength": 1},
                    "type": {"type": "string", "enum": ["primary", "special"]},
                    "start_date": required_date,
                    "end_date": required_date,
                    "active": {"type": "boolean"},
                },
            },
        },
        "extras": extras,
    },
    "required": [
        "name",
        "division_id",
        "classification",
        "url",
    ],
}
