# type: ignore
# too many django types in this to type for now
from ..metadata import STATES_BY_ABBR
from ..utils.django import init_django
from django.core import management
from django.db import transaction  # type: ignore


def create_division(division_id: str, name: str):
    from ..data.models import Division

    return Division.objects.get_or_create(
        id=division_id,
        country="us",
        # TODO: allow changing name
        defaults=dict(name=name),
    )[0]


def create_chamber(juris, parent, chamber) -> None:
    from ..data.models import Organization, Post

    if chamber.chamber_type != "unicameral":
        post_parent, created = Organization.objects.get_or_create(
            id=chamber.organization_id,
            classification=chamber.chamber_type,
            parent_id=parent.id,
            jurisdiction_id=juris.id,
            name=chamber.name,
        )
    else:
        # parent is unicameral org
        post_parent = parent

    # create divisions and posts
    for district in chamber.districts:
        post_div = create_division(
            district.division_id, f"{juris.name} {chamber.name} {district.name}"
        )
        Post.objects.get_or_create(
            label=district.name,
            organization=post_parent,
            division=post_div,
            # TODO: allow changing role & max_memberships
            defaults=dict(
                role=district.title_override or chamber.title,
                maximum_memberships=district.num_seats,
            ),
        )


def create_full_jurisdiction(state) -> None:
    from ..data.models import Jurisdiction, Organization

    div = create_division(state.division_id, state.name)
    juris, created = Jurisdiction.objects.get_or_create(
        id=state.jurisdiction_id,
        name=state.name,
        division=div,
        classification="state" if state.abbr != "US" else "country",
        defaults=dict(url=state.url),
    )
    leg, created = Organization.objects.get_or_create(
        id=state.legislature_organization_id,
        classification="legislature",
        jurisdiction=juris,
        defaults=dict(name=state.legislature_name),
    )
    # create executive
    Organization.objects.get_or_create(
        id=state.executive_organization_id,
        classification="executive",
        jurisdiction=juris,
        defaults=dict(name=state.executive_name),
    )

    if state.unicameral:
        create_chamber(juris, leg, state.legislature)
    else:
        create_chamber(juris, leg, state.lower)
        create_chamber(juris, leg, state.upper)


def load_jurisdictions() -> None:
    for name, state in STATES_BY_ABBR.items():
        print("loading", name)
        create_full_jurisdiction(state)


def main() -> None:
    init_django()
    management.call_command("migrate")
    with transaction.atomic():
        load_jurisdictions()
