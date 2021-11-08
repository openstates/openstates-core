from .common import extras, fuzzy_date_string

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
                    "start_date": {
                        "type": [fuzzy_date_string, "date"],
                        "required": True,
                    },
                    "end_date": {"type": [fuzzy_date_string, "date"], "required": True},
                    "active": {"type": "boolean"},
                },
            },
        },
        "extras": extras,
    },
}
