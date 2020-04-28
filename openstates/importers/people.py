from django.db.models import Q
from .base import BaseImporter
from ..data.models import Person


class PersonImporter(BaseImporter):
    _type = "person"
    model_class = Person

    def limit_spec(self, spec):
        """
        Whenever we do a Pseudo ID lookup from the database, we need to limit
        based on the memberships -> organization -> jurisdiction, so we scope
        the resolution.
        """
        if list(spec.keys()) == ["name"]:
            # if we're just resolving on name, include other names and family name
            name = spec["name"]
            return (Q(name=name) | Q(other_names__name=name) | Q(family_name=name)) & Q(
                memberships__organization__jurisdiction_id=self.jurisdiction_id
            )
        spec["memberships__organization__jurisdiction_id"] = self.jurisdiction_id
        return spec
