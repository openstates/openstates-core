"""
    Schema for bill objects.
"""
import copy
from .common import (
    sources,
    extras,
    fuzzy_date_blank,
    fuzzy_datetime,
    jurisdiction_summary,
)
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
                },
                "type": "array",
            },
        },
        "type": "object",
    },
    "type": "array",
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
    "type": "object",
    "properties": {
        "legislative_session": {"type": "string", "minLength": 1},
        "identifier": {"type": "string", "minLength": 1},
        "title": {"type": "string", "minLength": 1},
        "from_organization": {"type": ["string", "null"]},
        "classification": {
            "items": {"type": "string", "enum": common.BILL_CLASSIFICATIONS},
            "type": "array",
        },
        "subject": {"items": {"type": "string", "minLength": 1}, "type": "array"},
        "abstracts": {
            "items": {
                "properties": {
                    "abstract": {"type": "string", "minLength": 1},
                    "note": {"type": "string"},
                    "date": {"type": "string"},
                },
                "type": "object",
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
            },
            "type": "array",
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
        "jurisdiction": jurisdiction_summary,
        "scraped_at": fuzzy_datetime,
    },
}
