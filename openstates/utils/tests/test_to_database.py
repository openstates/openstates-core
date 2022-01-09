import pytest  # type: ignore
from openstates.data.models import Organization, Jurisdiction, Division
from openstates.data.models import Person as DjangoPerson
from openstates.utils.people.to_database import load_person, cached_lookup
from openstates.models.people import (
    Person,
    Party,
    Link,
    Role,
    OtherName,
    OtherIdentifier,
    Office,
)
from openstates.models.committees import Committee, Membership
from openstates.cli.committees import committee_to_db, _parent_lookup


def setup():
    d = Division.objects.create(id="ocd-division/country:us/state:nc", name="NC")
    j = Jurisdiction.objects.create(
        id="ocd-jurisdiction/country:us/state:nc/government", name="NC", division=d
    )
    o = Organization.objects.create(
        name="House", classification="lower", jurisdiction=j
    )
    for n in range(1, 4):
        division = Division.objects.create(
            id=f"ocd-division/country:us/state:nc/sldl:{n}", name=str(n)
        )
        o.posts.create(label=str(n), division=division)
    Organization.objects.create(
        name="Executive", classification="executive", jurisdiction=j
    )
    Organization.objects.create(name="Democratic", classification="party")
    Organization.objects.create(name="Republican", classification="party")
    j2 = Jurisdiction.objects.create(
        id="ocd-jurisdiction/country:us/state:nc/place:cary/government", name="Cary, NC"
    )
    Organization.objects.create(
        name="Cary Town Government", classification="government", jurisdiction=j2
    )

    # clear cache here because we can't have lru_cache keep the old party ids, etc. around
    # between tests as setup() is called once per test
    cached_lookup.cache_clear()
    _parent_lookup.cache_clear()


@pytest.fixture
def person():
    PERSON_ID = "ocd-person/abcdefab-0000-1111-2222-1234567890ab"
    return Person(
        id=PERSON_ID,
        name="Jane Smith",
        party=[Party(name="Democratic")],
        roles=[],
        image="https://example.com/image",
        extras={"something": "special"},
    )


@pytest.mark.django_db
def test_basic_person_creation(person):
    created, updated = load_person(person)

    assert created is True
    p = DjangoPerson.objects.get(pk=person.id)
    assert p.name == "Jane Smith"
    assert p.image == "https://example.com/image"
    assert p.extras["something"] == "special"
    assert p.current_role is None


@pytest.mark.django_db
def test_basic_person_updates(person):
    created, updated = load_person(person)
    p = DjangoPerson.objects.get(pk=person.id)
    created_at, updated_at = p.created_at, p.updated_at

    # ensure no change means no change
    created, updated = load_person(person)
    assert created is False
    assert updated is False
    p = DjangoPerson.objects.get(pk=person.id)
    assert p.created_at == created_at
    assert p.updated_at == updated_at

    # ensure extra changes got captured
    person.extras["something"] = "changed"
    created, updated = load_person(person)
    assert created is False
    assert updated is True
    p = DjangoPerson.objects.get(pk=person.id)
    assert p.updated_at > updated_at
    assert p.extras["something"] == "changed"


@pytest.mark.django_db
def test_basic_person_subobjects(person):
    person.links = [
        Link(url="https://example.com"),
        Link(url="https://example.com/2", note="some additional data"),
    ]
    person.sources = [Link(url="https://example.com/jane")]
    person.other_names = [
        OtherName(name="J. Smith"),
    ]

    created, updated = load_person(person)
    p = DjangoPerson.objects.get(pk=person.id)

    assert p.links.count() == 2
    assert p.links.filter(note="some additional data").count() == 1
    assert p.sources.count() == 1
    assert p.other_names.count() == 1


@pytest.mark.django_db
def test_subobject_update(person):
    person.links = [
        Link(url="https://example.com"),
        Link(url="https://example.com/2", note="some additional data"),
    ]
    created, updated = load_person(person)
    p = DjangoPerson.objects.get(pk=person.id)
    created_at, updated_at = p.created_at, p.updated_at

    # ensure no change means no change
    created, updated = load_person(person)
    assert created is False
    assert updated is False
    p = DjangoPerson.objects.get(pk=person.id)
    assert p.created_at == created_at
    assert p.updated_at == updated_at

    # change one field
    person.links[0].url = "https://example.com/jane-smith"
    created, updated = load_person(person)

    assert created is False
    assert updated is True
    p = DjangoPerson.objects.get(pk=person.id)
    assert p.links.count() == 2
    assert p.links.filter(url="https://example.com/jane-smith").count() == 1
    assert p.updated_at > updated_at

    # delete a field
    person.links.pop()
    created, updated = load_person(person)
    assert created is False
    assert updated is True
    p = DjangoPerson.objects.get(pk=person.id)
    assert p.links.count() == 1
    assert p.updated_at > updated_at


@pytest.mark.django_db
def test_subobject_duplicate(person):
    # this shouldn't actually be allowed most places (lint should catch)
    # but it was breaking committee imports when two members had the same name
    person.links = [
        Link(url="https://example.com"),
        Link(url="https://example.com"),
    ]
    # load twice, but second time no update should occur
    created, updated = load_person(person)
    created, updated = load_person(person)
    assert created is False
    assert updated is False


@pytest.mark.django_db
def test_person_identifiers(person):
    person.ids.twitter = "fakeaccount"
    person.ids.youtube = "fakeaccount"
    person.other_identifiers.append(
        OtherIdentifier(scheme="old_openstates", identifier="AR000001")
    )
    person.other_identifiers.append(
        OtherIdentifier(scheme="old_openstates", identifier="AR000002")
    )
    created, updated = load_person(person)
    p = DjangoPerson.objects.get(pk=person.id)

    assert p.identifiers.count() == 4
    assert p.identifiers.filter(scheme="old_openstates").count() == 2
    assert p.identifiers.filter(scheme="twitter")[0].identifier == "fakeaccount"


@pytest.mark.django_db
def test_person_offices(person):
    person.email = "fake@example.com"
    person.offices.append(
        Office(
            classification="capitol",
            fax="111-222-3333",
            voice="555-555-5555",
            address="123 Main St; Washington DC",
        )
    )
    person.offices.append(
        Office(
            classification="primary",
            voice="333-333-5555",
        )
    )

    created, updated = load_person(person)
    p = DjangoPerson.objects.get(pk=person.id)

    assert p.email == "fake@example.com"
    assert p.offices.count() == 2


@pytest.mark.django_db
def test_person_party(person):
    created, updated = load_person(person)
    p = DjangoPerson.objects.get(pk=person.id)

    assert p.memberships.count() == 1
    assert p.memberships.get().organization.name == "Democratic"
    assert p.primary_party == "Democratic"

    person.party.append(Party(name="Republican", end_date="2018-10-06"))
    created, updated = load_person(person)
    assert updated is True
    assert p.primary_party == "Democratic"
    p = DjangoPerson.objects.get(pk=person.id)
    p.memberships.count() == 2
    p.memberships.exclude(end_date="").count() == 1


@pytest.mark.django_db
def test_person_legislative_roles(person):
    person.roles.append(
        Role(
            type="lower",
            district=3,
            jurisdiction="ocd-jurisdiction/country:us/state:nc/government",
        )
    )
    created, updated = load_person(person)
    p = DjangoPerson.objects.get(pk=person.id)

    # party and legislative
    assert p.memberships.count() == 2
    assert (
        p.memberships.get(organization__classification="lower").organization.name
        == "House"
    )
    assert p.memberships.get(organization__classification="lower").post.label == "3"
    assert p.current_role == {
        "org_classification": "lower",
        "district": 3,
        "division_id": "ocd-division/country:us/state:nc/sldl:3",
        "title": "Representative",
    }
    assert (
        p.current_jurisdiction_id == "ocd-jurisdiction/country:us/state:nc/government"
    )


@pytest.mark.django_db
def test_person_governor_role(person):
    person.roles.append(
        Role(
            type="governor",
            jurisdiction="ocd-jurisdiction/country:us/state:nc/government",
            end_date="2030-01-01",
        )
    )
    created, updated = load_person(person)
    p = DjangoPerson.objects.get(pk=person.id)

    assert p.memberships.count() == 2
    assert (
        p.memberships.get(organization__classification="executive").organization.name
        == "Executive"
    )
    assert p.current_role == {
        "org_classification": "executive",
        "district": None,
        "division_id": None,
        "title": "Governor",
    }
    assert (
        p.current_jurisdiction_id == "ocd-jurisdiction/country:us/state:nc/government"
    )


@pytest.mark.django_db
def test_person_mayor_role(person):
    person.roles.append(
        Role(
            type="mayor",
            jurisdiction="ocd-jurisdiction/country:us/state:nc/place:cary/government",
            end_date="2030-01-01",
        )
    )
    created, updated = load_person(person)
    p = DjangoPerson.objects.get(pk=person.id)

    assert p.memberships.count() == 2
    assert p.current_role == {
        "org_classification": "government",
        "district": None,
        "division_id": None,
        "title": "Mayor",
    }
    assert (
        p.current_jurisdiction_id
        == "ocd-jurisdiction/country:us/state:nc/place:cary/government"
    )


@pytest.mark.django_db
def test_committee_to_db_simple():
    com_id = "ocd-organization/00000000-1111-1111-1111-222222222222"
    new_com = Committee(
        id=com_id,
        name="Education",
        chamber="lower",
        jurisdiction="ocd-jurisdiction/country:us/state:nc/government",
        sources=[{"url": "https://example.com"}],
        members=[Membership(name="someone", role="member")],
    )
    created, updated = committee_to_db(new_com)
    assert created and not updated
    org = Organization.objects.get(pk=com_id)
    assert org.sources == new_com.sources

    new_com.links = [{"url": "https://example.com"}]
    created, updated = committee_to_db(new_com)
    assert updated and not created
    org = Organization.objects.get(pk=com_id)
    assert org.links == new_com.links


@pytest.mark.django_db
def test_committee_to_db_memberships():
    com_id = "ocd-organization/00000000-1111-1111-1111-222222222222"
    new_com = Committee(
        id=com_id,
        name="Education",
        chamber="lower",
        jurisdiction="ocd-jurisdiction/country:us/state:nc/government",
        members=[Membership(name="Steve", role="chair")],
    )
    created, updated = committee_to_db(new_com)
    org = Organization.objects.get(pk=com_id)
    assert org.memberships.count() == 1
    s_mem = org.memberships.get()
    assert s_mem.person_name == "Steve"
    assert s_mem.role == "chair"

    person_id = "ocd-person/33333333-4444-4444-4444-555555555555"
    wendy = DjangoPerson.objects.create(id=person_id, name="Wendy")
    new_com.add_member("Wendy", role="chair")
    new_com.members[-1].person_id = person_id
    created, updated = committee_to_db(new_com)
    assert updated and not created
    org = Organization.objects.get(pk=com_id)
    assert org.memberships.count() == 2
    w_mem = org.memberships.filter(person_name="Wendy")[0]
    assert w_mem.person == wendy


@pytest.mark.django_db
def test_no_person_updates_with_committee(person):
    created, updated = load_person(person)
    DjangoPerson.objects.get(pk=person.id)

    parent_com = Committee(
        id="ocd-organization/00000000-1111-1111-1111-222222222222",
        name="Finance",
        chamber="lower",
        jurisdiction="ocd-jurisdiction/country:us/state:nc/government",
        members=[Membership(name="Steve", role="chair")],
    )
    created, updated = committee_to_db(parent_com)

    sub_com = Committee(
        id="ocd-organization/00000000-1111-1111-1111-333333333333",
        name="Education",
        chamber="lower",
        classification="subcommittee",
        parent="ocd-organization/00000000-1111-1111-1111-222222222222",
        jurisdiction="ocd-jurisdiction/country:us/state:nc/government",
        members=[Membership(name="Steve", role="chair", person_id=person.id)],
    )
    created, updated = committee_to_db(sub_com)
    assert created and not updated

    created, updated = load_person(person)
    assert not created and not updated
