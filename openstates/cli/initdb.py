from openstates_metadata import STATES_BY_ABBR
from ..utils.django import init_django


init_django()
from ..data.models import Jurisdiction, Division, Organization, Post  # noqa


def create_division(division_id, name):
    return Division.objects.get_or_create(
        id=division_id,
        defaults=dict(name=name, country="us"),
        # **Division.subtypes_from_id(division_id)[0]
    )[0]


def create_chamber(juris, parent, chamber):
    if chamber.chamber_type != "unicameral":
        post_parent = Organization.objects.create(
            id=chamber.organization_id,
            name=chamber.name,
            classification=chamber.chamber_type,
            parent_id=parent.id,
            jurisdiction_id=juris.id,
        )
    else:
        # parent is unicameral org
        post_parent = parent

    # create divisions and posts
    for district in chamber.districts:
        post_div = create_division(
            district.division_id, f"{juris.name} {chamber.name} {district.name}"
        )
        Post.objects.create(
            label=district.name,
            role=chamber.title,
            organization=post_parent,
            division=post_div,
            maximum_memberships=district.num_seats,
        )


def load_jurisdictions():
    for name, state in STATES_BY_ABBR.items():
        print("creating", name)

        div = create_division(state.division_id, state.name)
        juris = Jurisdiction.objects.create(
            id=state.jurisdiction_id, name=state.name, url=state.url, division=div
        )
        leg = Organization.objects.create(
            id=state.legislature_organization_id,
            name=state.legislature_name,
            classification="legislature",
            jurisdiction=juris,
        )
        # create executive
        Organization.objects.create(
            id=state.executive_organization_id,
            name=state.executive_name,
            classification="executive",
            jurisdiction=juris,
        )

        if state.unicameral:
            create_chamber(juris, leg, state.legislature)
        else:
            create_chamber(juris, leg, state.lower)
            create_chamber(juris, leg, state.upper)


def main():
    load_jurisdictions()
