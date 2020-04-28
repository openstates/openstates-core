from django.db.models import Q
from .base import BaseImporter
from ..data.models import Organization


class OrganizationImporter(BaseImporter):
    _type = "organization"
    model_class = Organization

    def limit_spec(self, spec):
        if spec.get("classification") != "party":
            spec["jurisdiction_id"] = self.jurisdiction_id

        name = spec.pop("name", None)
        if name:
            return Q(**spec) & Q(name=name)
        return spec
