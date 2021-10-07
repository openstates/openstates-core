import copy
from .base import BaseModel, SourceMixin, LinkMixin
from .schemas.organization import schema as org_schema
from ..utils import _make_pseudo_id
from ..exceptions import ScrapeValueError

# a copy of the org schema without sources
org_schema_no_sources = copy.deepcopy(org_schema)
org_schema_no_sources["properties"].pop("sources")


class Organization(BaseModel, SourceMixin, LinkMixin):
    """
    A single popolo-style Organization
    """

    _type = "organization"
    _schema = org_schema

    def __init__(self, name, *, classification="", parent_id=None, chamber=None):
        """
        Constructor for the Organization object.
        """
        super(Organization, self).__init__()
        self.name = name
        self.classification = classification
        self.parent_id = pseudo_organization(parent_id, chamber)

    def __str__(self):
        return self.name

    def validate(self):
        schema = None
        # these are implicitly declared & do not require sources
        if self.classification in (
            "party",
            "legislature",
            "upper",
            "lower",
            "executive",
        ):
            schema = org_schema_no_sources
        return super(Organization, self).validate(schema=schema)

    def add_post(self, label, role, **kwargs):
        # STUB: will be removed soon
        pass

    def add_member(self, name_or_person, role="member", **kwargs):
        # STUB: will be removed soon
        pass


def pseudo_organization(organization, classification, default=None):
    """helper for setting an appropriate ID for organizations"""
    if organization and classification:
        raise ScrapeValueError("cannot specify both classification and organization")
    elif classification:
        return _make_pseudo_id(classification=classification)
    elif organization:
        if isinstance(organization, Organization):
            return organization._id
        elif isinstance(organization, str):
            return organization
        else:
            return _make_pseudo_id(**organization)
    elif default is not None:
        return _make_pseudo_id(classification=default)
    else:
        return None
