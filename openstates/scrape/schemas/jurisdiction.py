from .common import extras, fuzzy_date

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
                    "start_date": fuzzy_date,
                    "end_date": fuzzy_date,
                    "active": {"type": "boolean"},
                },
                "required": ["start_date", "end_date"],
            },
        },
        "extras": extras,
    },
    "required": [
        "name",
        "division_id",
        "classification",
        "url",
        "legislative_sessions",
    ],
}
