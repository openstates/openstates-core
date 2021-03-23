import pytest
from openstates.data.models import Jurisdiction, Division, Organization, Post
from openstates.cli.initdb import (
    create_division,
    create_chamber,
    create_full_jurisdiction,
)
from openstates.metadata import lookup
from django.db.utils import IntegrityError


@pytest.mark.django_db
def test_create_division_basic():
    div = create_division("ocd-division/country:us/state:nc", "North Carolina")
    assert div.name == "North Carolina"
    assert Division.objects.count() == 1


@pytest.mark.django_db
def test_create_division_duplicate():
    div = create_division("ocd-division/country:us/state:nc", "North Carolina")
    # first name persists b/c of get_or_create
    div = create_division("ocd-division/country:us/state:nc", "N. Carolina")
    assert div.name == "North Carolina"
    assert Division.objects.count() == 1


@pytest.mark.django_db
def test_create_chamber_basic():
    nc = lookup(abbr="NC")

    juris = Jurisdiction.objects.create(
        id=nc.jurisdiction_id, name=nc.name, division=None
    )
    leg = Organization.objects.create(
        id=nc.legislature_organization_id,
        name=nc.legislature_name,
        classification="legislature",
        jurisdiction=juris,
    )
    create_chamber(juris, leg, nc.lower)

    # ensure the org and posts were created
    org = Organization.objects.get(classification="lower")
    assert org.name == nc.lower.name
    assert org.id == nc.lower.organization_id
    assert org.posts.count() == 120


@pytest.mark.django_db
def test_create_chamber_duplicate_idempotent():
    nc = lookup(abbr="NC")

    juris = Jurisdiction.objects.create(
        id=nc.jurisdiction_id, name=nc.name, division=None
    )
    leg = Organization.objects.create(
        id=nc.legislature_organization_id,
        name=nc.legislature_name,
        classification="legislature",
        jurisdiction=juris,
    )

    # second call, identical to first, should be idempotent
    create_chamber(juris, leg, nc.lower)
    create_chamber(juris, leg, nc.lower)

    assert Organization.objects.filter(classification="lower").count() == 1

    # ensure the org and posts were created
    org = Organization.objects.get(classification="lower")
    assert org.name == nc.lower.name
    assert org.id == nc.lower.organization_id
    assert org.posts.count() == 120


@pytest.mark.django_db
def test_create_chamber_duplicate_with_changes():
    nc = lookup(abbr="NC")

    juris = Jurisdiction.objects.create(
        id=nc.jurisdiction_id, name=nc.name, division=None
    )
    leg = Organization.objects.create(
        id=nc.legislature_organization_id,
        name=nc.legislature_name,
        classification="legislature",
        jurisdiction=juris,
    )

    create_chamber(juris, leg, nc.lower)
    # second call, but lower chamber name has been changed
    nc.lower.name = "Ronald McDonald House of Clowns"
    with pytest.raises(IntegrityError):
        create_chamber(juris, leg, nc.lower)  # unsupported, should definitely be loud

    assert Organization.objects.filter(classification="lower").count() == 1


@pytest.mark.django_db
def test_create_chamber_unicam():
    ne = lookup(abbr="NE")

    juris = Jurisdiction.objects.create(
        id=ne.jurisdiction_id, name=ne.name, division=None
    )
    leg = Organization.objects.create(
        id=ne.legislature_organization_id,
        name=ne.legislature_name,
        classification="legislature",
        jurisdiction=juris,
    )

    create_chamber(juris, leg, ne.legislature)

    # no org was created, but posts were
    assert Organization.objects.count() == 1
    org = Organization.objects.get(classification="legislature")
    assert org.posts.count() == 49


@pytest.mark.django_db
def test_create_full_jurisdiction_basic():
    nc = lookup(abbr="NC")
    create_full_jurisdiction(nc)

    assert Jurisdiction.objects.count() == 1
    juris = Jurisdiction.objects.get()
    assert juris.name == nc.name
    assert juris.organizations.count() == 4
    assert (
        juris.organizations.get(classification="executive").id
        == nc.executive_organization_id
    )
    assert (
        juris.organizations.get(classification="legislature").id
        == nc.legislature_organization_id
    )
    # 120 + 50
    assert Post.objects.count() == 170


@pytest.mark.django_db
def test_create_full_jurisdiction_idempotent():
    nc = lookup(abbr="NC")
    create_full_jurisdiction(nc)
    # second call, does nothing
    create_full_jurisdiction(nc)

    assert Jurisdiction.objects.count() == 1
    juris = Jurisdiction.objects.get()
    assert juris.name == nc.name
    assert juris.organizations.count() == 4
    assert (
        juris.organizations.get(classification="executive").id
        == nc.executive_organization_id
    )
    assert (
        juris.organizations.get(classification="legislature").id
        == nc.legislature_organization_id
    )
    # 120 + 50
    assert Post.objects.count() == 170


@pytest.mark.django_db
def test_create_federal_jurisdiction():
    us = lookup(abbr="US")
    create_full_jurisdiction(us)

    assert Jurisdiction.objects.count() == 1
    juris = Jurisdiction.objects.get()
    assert juris.name == us.name
    assert juris.classification == "country"
    assert juris.organizations.count() == 4
    assert (
        juris.organizations.get(classification="executive").id
        == us.executive_organization_id
    )
    assert (
        juris.organizations.get(classification="legislature").id
        == us.legislature_organization_id
    )
    # 435 House + 50 Senate posts + 2 territories (DC & PR for now)
    assert Post.objects.filter(role="Representative").count() == 435
    assert Post.objects.filter(role="Senator").count() == 50
    assert Post.objects.filter(role="Delegate").count() == 1
    assert Post.objects.filter(role="Resident Commissioner").count() == 1
