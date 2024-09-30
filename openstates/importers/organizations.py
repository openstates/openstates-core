from django.db.models import Q
from ._types import _JsonDict
from .base import BaseImporter
from ..data.models import Organization


class OrganizationImporter(BaseImporter):
    _type = "organization"
    model_class = Organization

    def limit_spec(self, spec: _JsonDict) -> _JsonDict:
        if spec.get("classification") != "party":
            spec["jurisdiction_id"] = self.jurisdiction_id

        name = spec.pop("name", None)
        if name:
            # __icontains doesn't work for JSONField ArrayField
            # so other_name_lowercase_on follows "title" naming pattern
            other_name_lowercase_on = name.title().replace(" On ", " on ")
            return Q(**spec) & (
                Q(name__iexact=name)
                | Q(other_names__contains=[{"name": other_name_lowercase_on}])
            )
        return spec
