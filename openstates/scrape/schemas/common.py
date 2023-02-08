fuzzy_date_string = {"type": "string", "pattern": "^[0-9]{4}(-[0-9]{2}){0,2}$"}
fuzzy_date_string_blank = {"type": "string", "pattern": "^([0-9]{4})?(-[0-9]{2}){0,2}$"}
fuzzy_datetime_string_blank = {
    "type": "string",
    "pattern": (
        "^([0-9]{4}((-[0-9]{2}){0,2}|(-[0-9]{2}){2}T"
        "[0-9]{2}(:[0-9]{2}){0,2}"
        "(Z|[+-][0-9]{2}(:[0-9]{2})?))?)?$"
    ),
}

"""
anyOf schema settings allow us to define mutiple types
for one value
"""
fuzzy_date = {"anyOf": [fuzzy_date_string, {"type": "object", "format": "python-date"}]}
fuzzy_date_blank = {
    "anyOf": [
        fuzzy_date_string_blank,
        {"type": "null"},
        {"type": "object", "format": "python-date"},
    ]
}
fuzzy_datetime = {
    "anyOf": [
        fuzzy_datetime_string_blank,
        {"type": "object", "format": "python-datetime"},
    ]
}
fuzzy_datetime_blank = {
    "anyOf": [
        fuzzy_datetime_string_blank,
        {"type": "null"},
        {"type": "object", "format": "python-datetime"},
    ]
}

"""
General Sub-schemas
"""
identifiers = {
    "items": {
        "properties": {
            "identifier": {"type": "string", "minLength": 1},
            "scheme": {"type": "string"},
        }
    },
    "type": "array",
}

other_names = {
    "items": {
        "properties": {
            "name": {"type": "string", "minLength": 1},
            "start_date": fuzzy_date_blank,
            "end_date": fuzzy_date_blank,
            "note": {"type": "string"},
        },
        "type": "object",
        "required": ["name"],
    },
    "type": "array",
}


links = {
    "items": {
        "properties": {
            "note": {"type": "string"},
            "url": {"format": "uri", "type": "string"},
        },
        "type": "object",
        "required": ["url"],
    },
    "type": "array",
}


sources = {
    "items": {
        "properties": {
            "url": {"type": "string", "format": "uri"},
            "note": {"type": "string"},
        },
        "type": "object",
        "required": ["url"],
    },
    "minItems": 1,
    "type": "array",
    "description": "An array of objects representing data sources where this data was found",
}

extras = {"type": "object"}
