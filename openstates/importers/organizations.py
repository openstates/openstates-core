import re
from django.db.models import BooleanField, Q
from django.db.models.expressions import RawSQL
from ._types import _JsonDict
from .base import BaseImporter
from ..data.models import Organization

# Matches any "&" surrounded by optional whitespace, so it can be expanded
# to " and " before punctuation is stripped (otherwise "Fish & Game" and
# "Fish and Game" would normalize to different strings: "FISH GAME" vs
# "FISH AND GAME").
_AMPERSAND_RE = re.compile(r"\s*&\s*")

# Matches everything except letters, digits, and whitespace - used to
# compare organization names without regard to punctuation (commas,
# apostrophes, periods, etc). Keeping the Python and SQL normalization in
# sync is important: both sides of the comparison must use the same rule.
_NON_ALPHANUMERIC_RE = re.compile(r"[^A-Za-z0-9 ]")

# Collapses runs of whitespace down to a single space (ampersand expansion
# above can introduce extra spaces, e.g. "A&B" -> "A and B").
_EXTRA_WHITESPACE_RE = re.compile(r"\s+")

# The equivalent normalization expressed as a chain of Postgres
# regexp_replace calls, so we can apply it to `name` and to each entry of
# the `other_names` JSONB array. `{column}` is substituted with the SQL
# expression for the column/value being normalized.
_NORMALIZE_SQL_TEMPLATE = """
    upper(trim(regexp_replace(
        regexp_replace(
            regexp_replace({column}, '\\s*&\\s*', ' and ', 'g'),
            '[^A-Za-z0-9 ]', '', 'g'
        ),
        '\\s+', ' ', 'g'
    )))
"""

# Raw SQL boolean expression used to find organizations whose `name` OR any
# entry in the `other_names` JSONB array matches a normalized name. This
# avoids trying to guess the exact case/punctuation used in `other_names`
# (which is free-form, human-entered data from the people repo) - instead
# both sides are normalized (uppercased, punctuation stripped, "&"
# expanded to "and") before comparison.
_NORMALIZED_NAME_MATCH_SQL = f"""
    {_NORMALIZE_SQL_TEMPLATE.format(column="name")} = %s
    OR EXISTS (
        SELECT 1 FROM jsonb_array_elements(other_names) AS other_name
        WHERE {_NORMALIZE_SQL_TEMPLATE.format(column="other_name ->> 'name'")} = %s
    )
"""


def _normalize_name(name: str) -> str:
    """Normalize an organization name for comparison purposes: expand "&"
    to "and", strip punctuation, collapse whitespace, and uppercase. This
    must stay equivalent to the Postgres expression in
    _NORMALIZE_SQL_TEMPLATE."""
    name = _AMPERSAND_RE.sub(" and ", name)
    name = _NON_ALPHANUMERIC_RE.sub("", name)
    name = _EXTRA_WHITESPACE_RE.sub(" ", name)
    return name.strip().upper()


class OrganizationImporter(BaseImporter):
    _type = "organization"
    model_class = Organization

    def limit_spec(self, spec: _JsonDict) -> _JsonDict:
        if spec.get("classification") != "party":
            spec["jurisdiction_id"] = self.jurisdiction_id

        name = spec.pop("name", None)
        # if chamber is included in pseudo_person_id, we assume this is a committee
        # and chamber is here to help us find its parent
        chamber_classification = spec.pop("chamber", None)
        if name:
            normalized_name = _normalize_name(name)
            matching_orgs = Organization.objects.annotate(
                _normalized_name_match=RawSQL(
                    _NORMALIZED_NAME_MATCH_SQL,
                    (normalized_name, normalized_name),
                    output_field=BooleanField(),
                )
            ).filter(_normalized_name_match=True)
            name_q = Q(pk__in=matching_orgs)

            if chamber_classification:
                return (
                    Q(**spec)
                    & name_q
                    & Q(parent__classification=chamber_classification)
                )
            else:
                return Q(**spec) & name_q
        return spec
