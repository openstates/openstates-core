from .base import BaseImporter
from ._types import _JsonDict, Model
from ..exceptions import InternalError
from ..data.models import (
    Bill,
    RelatedBill,
    BillAbstract,
    BillTitle,
    BillIdentifier,
    BillAction,
    BillActionRelatedEntity,
    BillSponsorship,
    BillSource,
    BillDocument,
    BillVersion,
    BillDocumentLink,
    BillVersionLink,
)
from .computed_fields import update_bill_fields
from .organizations import OrganizationImporter


def resolve_related_bills(jurisdiction_id, logger) -> None:
    # go through all RelatedBill objs that are attached to a bill in this jurisdiction and
    # are currently unresolved
    related_bills = RelatedBill.objects.filter(
        bill__legislative_session__jurisdiction_id=jurisdiction_id,
        related_bill=None,
    )
    logger.info(f"Found {len(related_bills)} unresolved bill relationships")
    matches_found = 0
    for rb in related_bills:
        candidates = list(
            Bill.objects.filter(
                legislative_session__identifier=rb.legislative_session,
                legislative_session__jurisdiction_id=jurisdiction_id,
                identifier=rb.identifier,
            )
        )
        if len(candidates) == 1:
            rb.related_bill = candidates[0]
            rb.save()
            matches_found += 1
            logger.debug(f"Resolved {rb.legislative_session} {rb.bill.identifier}")
        elif len(candidates) > 1:  # pragma: no cover
            # if we ever see this, we need to add additional fields on the relation
            raise InternalError(
                "multiple related_bill candidates found for {}".format(rb)
            )
        else:
            logger.debug(f"FAILED to resolve {rb.legislative_session} {rb.bill.identifier}")

    logger.info(f"Resolved {matches_found} bills out of {len(related_bills)} bills needing resolution")


class BillImporter(BaseImporter):
    _type = "bill"
    model_class = Bill
    related_models = {
        "abstracts": (BillAbstract, "bill_id", {}),
        "other_titles": (BillTitle, "bill_id", {}),
        "other_identifiers": (BillIdentifier, "bill_id", {}),
        "actions": (
            BillAction,
            "bill_id",
            {"related_entities": (BillActionRelatedEntity, "action_id", {})},
        ),
        "related_bills": (RelatedBill, "bill_id", {}),
        "sponsorships": (BillSponsorship, "bill_id", {}),
        "sources": (BillSource, "bill_id", {}),
        "documents": (
            BillDocument,
            "bill_id",
            {"links": (BillDocumentLink, "document_id", {})},
        ),
        "versions": (
            BillVersion,
            "bill_id",
            {"links": (BillVersionLink, "version_id", {})},
        ),
    }
    preserve_order = {"actions"}

    def __init__(self, jurisdiction_id: str, do_postimport=True):
        super(BillImporter, self).__init__(jurisdiction_id, do_postimport)
        self.org_importer = OrganizationImporter(jurisdiction_id)

    def get_object(self, bill: _JsonDict) -> Model:
        spec = {
            "legislative_session_id": bill["legislative_session_id"],
            "identifier": bill["identifier"],
        }
        # bills should be unique per session + identifier, no need to use organization
        #   (note: this used to be different, but allowed duplicates)

        return self.model_class.objects.prefetch_related(
            "actions__related_entities", "versions__links", "documents__links"
        ).get(**spec)

    def limit_spec(self, spec: _JsonDict) -> _JsonDict:
        spec["legislative_session__jurisdiction_id"] = self.jurisdiction_id
        return spec

    def prepare_for_db(self, data: _JsonDict) -> _JsonDict:
        session = self.get_session(data.pop("legislative_session"))
        data["legislative_session_id"] = session.id

        if data["from_organization"]:
            data["from_organization_id"] = self.org_importer.resolve_json_id(
                data.pop("from_organization")
            )

        for action in data["actions"]:
            action["organization_id"] = self.org_importer.resolve_json_id(
                action["organization_id"]
            )
            for entity in action["related_entities"]:
                if "organization_id" in entity:
                    entity["organization_id"] = self.org_importer.resolve_json_id(
                        entity["organization_id"]
                    )
                elif "person_id" in entity:
                    entity["person_id"] = self.resolve_person(
                        entity["person_id"], session.start_date, session.end_date
                    )

        for sponsor in data["sponsorships"]:
            if sponsor.get("person_id"):
                sponsor["person_id"] = self.resolve_person(
                    sponsor["person_id"],
                    session.start_date,
                    session.end_date,
                )
            if sponsor.get("organization_id"):
                sponsor["organization_id"] = self.org_importer.resolve_json_id(
                    sponsor["organization_id"], allow_no_match=True
                )

        return data

    def postimport(self) -> None:
        resolve_related_bills(self.jurisdiction_id, self.logger)

    def update_computed_fields(self, obj: Model) -> None:
        update_bill_fields(obj, save=False)
