import re
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

        org_name_prepositions = ["and", "at", "by", "for", "in", "on", "of", "the"]
        name = spec.pop("name", None)
        if name:
            # __icontains doesn't work for JSONField ArrayField
            # so name follows "title" naming pattern
            name = name.title()
            pattern = '(' + '|'.join(org_name_prepositions) + ')'
            name = re.sub(pattern, lambda match: match.group(0).lower(), name, flags=re.IGNORECASE)
            name = name.replace(" & ", " and ")

            return Q(**spec) & (
                Q(name__iexact=name)
                | Q(other_names__contains=[{"name": name}])
            )
        return spec
