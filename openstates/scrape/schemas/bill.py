"""
    Schema for bill objects.
"""
import copy
from .common import sources, extras, fuzzy_date_blank, fuzzy_datetime
from ...data import common

versions_or_documents = {
    "items": {
        "properties": {
            "note": {"type": "string", "minLength": 1},
            "date": fuzzy_date_blank,
            "classification": {"type": "string"},
            "links": {
                "items": {
                    "properties": {
                        "media_type": {"type": "string"},
                        "url": {"type": "string", "format": "uri"},
                    },
                    "type": "object",
                    "required": ["url"],
                },
                "type": "array",
            },
        },
        "type": "object",
        "required": ["note", "date", "links"],
    },
    "type": "array",
    "description": "An array of versions, each representing a version of the text of the bill",
}
versions = copy.deepcopy(versions_or_documents)
versions["items"]["properties"]["classification"][
    "enum"
] = common.BILL_VERSION_CLASSIFICATIONS
documents = copy.deepcopy(versions_or_documents)
documents["items"]["properties"]["classification"][
    "enum"
] = common.BILL_DOCUMENT_CLASSIFICATIONS

schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "http://json-schema.org/draft-07/schema#",
    "title": "Bill",
    "description": "An Open Civic Data bill object",
    "type": "object",
    "properties": {
        "legislative_session": {
            "type": "string",
            "minLength": 1,
            "description": "String uniquely identifying this legislative session within the jurisdiction",
        },
        "identifier": {
            "type": "string",
            "minLength": 1,
            "description": "String uniquely identifying this bill within this legislative session as presented by the data source, (e.g. HF 1)",
        },
        "title": {
            "type": "string",
            "minLength": 1,
            "description": "Title of the bill, as presented by the data source",
        },
        "from_organization": {
            "type": ["string", "null"],
            "description": "A serialized JSON object with the property of classification: lower/upper (???)",
        },
        "classification": {
            "items": {
                "type": "string",
                "minItems": 1,
                "enum": common.BILL_CLASSIFICATIONS,
            },
            "type": "array",
            "description": "An array of labels that classify the type of bill this is, (e.g. 'bill' or 'constitutional amendment'",
        },
        "subject": {
            "items": {"type": "string", "minLength": 1},
            "type": "array",
            "description": "An array of subject or topic strings provided by the data source",
        },
        "abstracts": {
            "items": {
                "properties": {
                    "abstract": {"type": "string", "minLength": 1},
                    "note": {"type": "string"},
                    "date": {"type": "string", "format": "date"},
                },
                "type": "object",
                "required": ["abstract"],
            },
            "type": "array",
        },
        "other_titles": {
            "items": {
                "properties": {
                    "title": {"type": "string", "minLength": 1},
                    "note": {"type": "string"},
                },
                "type": "object",
                "required": ["title"],
            },
            "type": "array",
        },
        "other_identifiers": {
            "items": {
                "properties": {
                    "identifier": {"type": "string", "minLength": 1},
                    "note": {"type": "string"},
                    "scheme": {"type": "string"},
                },
                "type": "object",
                "required": ["identifier"],
            },
            "type": "array",
        },
        "actions": {
            "items": {
                "properties": {
                    "organization": {"type": ["string", "null"]},
                    "date": fuzzy_datetime,
                    "description": {"type": "string", "minLength": 1},
                    "classification": {
                        "items": {
                            "type": "string",
                            "enum": common.BILL_ACTION_CLASSIFICATIONS,
                        },
                        "type": "array",
                    },
                    "related_entities": {
                        "items": {
                            "properties": {
                                "name": {"type": "string", "minLength": 1},
                                "entity_type": {
                                    "enum": ["organization", "person", ""],
                                    "type": "string",
                                },
                                "person_id": {"type": ["string", "null"]},
                                "organization_id": {"type": ["string", "null"]},
                            },
                            "type": "object",
                        },
                        "type": "array",
                    },
                },
                "type": "object",
                "required": ["description", "date"],
            },
            "type": "array",
            "description": "An array of actions, each representing an official action taken in the legislature on this bill",
        },
        "sponsorships": {
            "items": {
                "properties": {
                    "primary": {"type": "boolean"},
                    "classification": {"type": "string", "minLength": 1},
                    "name": {"type": "string", "minLength": 1},
                    "entity_type": {
                        "enum": ["organization", "person", ""],
                        "type": "string",
                    },
                    "person_id": {"type": ["string", "null"]},
                    "organization_id": {"type": ["string", "null"]},
                },
                "type": "object",
                "required": ["name", "classification", "entity_type", "primary"],
            },
            "type": "array",
        },
        "related_bills": {
            "items": {
                "properties": {
                    "identifier": {"type": "string", "minLength": 1},
                    "legislative_session": {"type": "string", "minLength": 1},
                    "relation_type": {
                        "enum": common.BILL_RELATION_TYPES,
                        "type": "string",
                    },
                },
                "type": "object",
                "required": ["identifier", "legislative_session", "relation_type"],
            },
            "type": "array",
        },
        "versions": versions,
        "documents": documents,
        "citations": {
            "items": {
                "properties": {
                    "publication": {"type": "string", "minLength": 1},
                    "citation": {"type": "string", "minLength": 1},
                    "citation_type": {
                        "enum": common.CITATION_TYPES,
                        "type": "string",
                    },
                    "effective": {"type": [fuzzy_date_blank, "null"]},
                    "expires": {"type": [fuzzy_date_blank, "null"]},
                    "url": {"type": ["string", "null"]},
                },
                "type": "object",
            },
            "type": "array",
        },
        "sources": sources,
        "extras": extras,
    },
    "required": [
        "title",
        "identifier",
        "legislative_session",
    ],
}
