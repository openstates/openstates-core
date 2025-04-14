import warnings
from ..utils import _make_pseudo_id, transformers
from .popolo import pseudo_organization
from .base import BaseModel, SourceMixin, AssociatedLinkMixin, cleanup_list
from .schemas.bill import schema


class Action(dict):
    def add_related_entity(self, name, entity_type, entity_id=None):
        ent = {"name": name, "entity_type": entity_type, entity_type + "_id": entity_id}
        self["related_entities"].append(ent)
        return ent


class Bill(SourceMixin, AssociatedLinkMixin, BaseModel):
    """
    An Open Civic Data bill.
    """

    _type = "bill"
    _schema = schema

    def __init__(
        self,
        identifier,
        legislative_session,
        title,
        *,
        chamber=None,
        from_organization=None,
        classification=None,
    ):
        super(Bill, self).__init__()

        self.identifier = identifier
        self.legislative_session = legislative_session
        self.title = title
        self.classification = cleanup_list(classification, ["bill"])
        self.from_organization = pseudo_organization(
            from_organization, chamber, "legislature"
        )

        self.actions = []
        self.other_identifiers = []
        self.other_titles = []
        self.documents = []
        self.related_bills = []
        self.sponsorships = []
        self.subject = []
        self.abstracts = []
        self.versions = []
        self.citations = []

    def pre_save(self, jurisdiction):
        # ensure subject is sorted for idempotent JSON output
        self.subject = sorted(self.subject)
        self.add_scrape_metadata(jurisdiction)

    def add_action(
        self,
        description,
        date,
        *,
        organization=None,
        chamber=None,
        classification=None,
        related_entities=None,
    ):
        action = Action(
            description=description,
            date=date,
            organization_id=pseudo_organization(organization, chamber, "legislature"),
            classification=cleanup_list(classification, []),
            related_entities=[],
        )
        self.actions.append(action)
        return action

    def add_citation(
        self,
        publication,
        citation,
        citation_type,
        *,
        effective=None,
        expires=None,
        url=None,
    ):
        self.citations.append(
            {
                "publication": publication,
                "citation": citation,
                "citation_type": citation_type,
                "effective": effective,
                "expires": expires,
                "url": url,
            }
        )

    def add_related_bill(self, identifier, legislative_session, relation_type):
        # Normalize identifier before saving
        identifier = transformers.fix_bill_id(identifier)

        # will we need jurisdiction, organization?
        self.related_bills.append(
            {
                "identifier": identifier,
                "legislative_session": legislative_session,
                "relation_type": relation_type,
            }
        )

    def add_sponsorship(
        self,
        name,
        classification,
        entity_type,
        primary,
        *,
        chamber=None,  # upper, lower or legislature
        entity_id=None,
    ):
        sp = {
            "name": name,
            "classification": classification,
            "entity_type": entity_type,
            "primary": primary,
            # set these so that all JSON objects have the same keys, prevents import errors
            "person_id": None,
            "organization_id": None,
        }
        # overwrite the id that exists
        if entity_type:
            if not entity_id:
                if chamber is not None:
                    entity_id = _make_pseudo_id(name=name, chamber=chamber)
                else:
                    entity_id = _make_pseudo_id(name=name)
            sp[entity_type + "_id"] = entity_id
        if sp in self.sponsorships:
            warnings.warn(f"duplicate sponsor {sp}", RuntimeWarning)
        self.sponsorships.append(sp)

    def add_sponsorship_by_identifier(
        self,
        name,
        classification,
        entity_type,
        primary,
        *,
        scheme,
        identifier,
        chamber=None,
    ):
        return self.add_sponsorship(
            name,
            classification,
            entity_type,
            primary,
            chamber=chamber,
            entity_id=_make_pseudo_id(
                identifiers__scheme=scheme, identifiers__identifier=identifier
            ),
        )

    def add_subject(self, subject):
        self.subject.append(subject)

    def add_abstract(self, abstract, note):
        self.abstracts.append({"note": note, "abstract": abstract})

    def add_title(self, title, note=""):
        self.other_titles.append({"note": note, "title": title})

    def add_identifier(self, identifier):
        self.other_identifiers.append({"identifier": identifier})

    def add_document_link(
        self,
        note,
        url,
        *,
        classification="",
        date="",
        media_type="",
        on_duplicate="warn",
    ):
        return self._add_associated_link(
            collection="documents",
            note=note,
            url=url,
            date=date,
            classification=classification,
            media_type=media_type,
            on_duplicate=on_duplicate,
        )

    def add_version_link(
        self,
        note,
        url,
        *,
        classification="",
        date="",
        media_type="",
        on_duplicate="warn",
    ):
        return self._add_associated_link(
            collection="versions",
            note=note,
            url=url,
            date=date,
            classification=classification,
            media_type=media_type,
            on_duplicate=on_duplicate,
        )

    def __str__(self):
        return self.identifier + " in " + self.legislative_session
