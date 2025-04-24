import pytest  # type: ignore
import datetime
from pathlib import Path
from openstates.utils.people.lint_people import (
    validate_name,
    validate_roles,
    validate_offices,
    get_expected_districts,
    compare_districts,
    Validator,
    BadVacancy,
    PersonType,
)  # noqa
from openstates.models.people import Person, Role, Party, Office


EXAMPLE_OCD_JURISDICTION_ID = "ocd-jurisdiction/country:us/government"
EXAMPLE_OCD_PERSON_ID = "ocd-person/12345678-0000-1111-2222-1234567890ab"
EXAMPLE_OCD_ORG_ID = "ocd-organization/00001111-2222-3333-aaaa-444455556666"


@pytest.mark.parametrize(
    "person,expected",
    [
        (Person(id=EXAMPLE_OCD_PERSON_ID, name="Phillip J Swoozle", roles=[]), []),
        (
            Person(id=EXAMPLE_OCD_PERSON_ID, name="Phillip Swoozle", roles=[]),
            [
                "missing given_name that could be set to 'Phillip', run with --fix",
                "missing family_name that could be set to 'Swoozle', run with --fix",
            ],
        ),
        (
            Person(
                id=EXAMPLE_OCD_PERSON_ID,
                name="Phillip Swoozle",
                given_name="Phil",
                roles=[],
            ),
            [
                "missing family_name that could be set to 'Swoozle', run with --fix",
            ],
        ),
        (
            Person(
                id=EXAMPLE_OCD_PERSON_ID,
                name="Phillip Swoozle",
                given_name="Phil",
                family_name="Swoozle",
                roles=[],
            ),
            [],
        ),
    ],
)
def test_validate_name_errors(person, expected):
    assert validate_name(person, PersonType.LEGISLATIVE, fix=False).errors == expected
    assert validate_name(person, PersonType.LEGISLATIVE, fix=False).warnings == []
    assert validate_name(person, PersonType.LEGISLATIVE, fix=False).fixes == []


def test_validate_name_fixes():
    person = Person(id=EXAMPLE_OCD_PERSON_ID, name="Phillip Swoozle", roles=[])
    result = validate_name(person, PersonType.LEGISLATIVE, fix=True)
    assert result.errors == []
    assert len(result.fixes) == 2
    assert person.given_name == "Phillip"
    assert person.family_name == "Swoozle"

    # no fixes on an OK name
    result = validate_name(person, PersonType.LEGISLATIVE, fix=True)
    assert result.errors == result.fixes == []


@pytest.mark.parametrize(
    "roles,expected",
    [
        (
            [Role(type="lower", jurisdiction=EXAMPLE_OCD_JURISDICTION_ID, district=3)],
            [],
        ),
        (
            [
                Role(
                    type="upper", jurisdiction=EXAMPLE_OCD_JURISDICTION_ID, district=3
                ),
                Role(
                    type="lower", jurisdiction=EXAMPLE_OCD_JURISDICTION_ID, district=3
                ),
            ],
            ["2 active roles"],
        ),
        ([], ["no active roles"]),
        (
            [
                Role(
                    type="governor",
                    jurisdiction=EXAMPLE_OCD_JURISDICTION_ID,
                    end_date="1990",
                )
            ],
            ["no active roles"],
        ),
    ],
)
def test_validate_roles_roles(roles, expected):
    person = Person(
        id=EXAMPLE_OCD_PERSON_ID,
        name="Example Person",
        roles=roles,
        party=[Party(name="Republican")],
    )
    assert validate_roles(person, "roles") == expected


@pytest.mark.parametrize(
    "roles,expected",
    [
        (
            [Role(type="lower", jurisdiction=EXAMPLE_OCD_JURISDICTION_ID, district=3)],
            ["1 active roles on retired person"],
        ),
        (
            [
                Role(
                    type="upper", jurisdiction=EXAMPLE_OCD_JURISDICTION_ID, district=3
                ),
                Role(
                    type="lower", jurisdiction=EXAMPLE_OCD_JURISDICTION_ID, district=3
                ),
            ],
            ["2 active roles on retired person"],
        ),
        ([], []),
        (
            [
                Role(
                    type="governor",
                    jurisdiction=EXAMPLE_OCD_JURISDICTION_ID,
                    end_date="1990",
                )
            ],
            [],
        ),
    ],
)
def test_validate_roles_retired(roles, expected):
    person = Person(
        id=EXAMPLE_OCD_PERSON_ID,
        name="Example Person",
        roles=roles,
        party=[Party(name="Republican")],
    )
    assert validate_roles(person, "roles", retired=True) == expected


@pytest.mark.parametrize(
    "offices,expected",
    [
        ([], []),
        (
            [
                {"classification": "district", "voice": "111-222-4333"},
                {"classification": "district", "voice": "555-555-5555"},
            ],
            [],
        ),
    ],
)
def test_validate_offices(offices, expected):
    person = Person(
        id=EXAMPLE_OCD_PERSON_ID,
        name="Example Person",
        roles=[],
        offices=[Office(**c) for c in offices],
    )
    assert validate_offices(person) == expected


def test_get_expected_districts():
    expected = get_expected_districts({}, "ne")
    assert len(expected["legislature"]) == 49
    assert expected["legislature"]["1"] == 1

    expected = get_expected_districts({}, "md")
    print(expected)
    assert expected["lower"]["43A"] == 2
    assert expected["lower"]["43B"] == 1


def test_expected_districts_vacancies():
    vacancies = {
        "ne": {
            "vacancies": [
                {
                    "chamber": "legislature",
                    "district": "1",
                    "vacant_until": datetime.date(2100, 1, 1),
                }
            ]
        }
    }
    expected = get_expected_districts(vacancies, "ne")
    assert expected["legislature"]["1"] == 0

    with pytest.raises(BadVacancy):
        get_expected_districts(
            {
                "ne": {
                    "vacancies": [
                        {
                            "chamber": "upper",
                            "district": "2",
                            "vacant_until": datetime.date(2000, 1, 1),
                        }
                    ]
                }
            },
            "ne",
        )


@pytest.mark.parametrize(
    "expected,actual,errors",
    [
        ({"A": 1, "B": 1}, {"A": ["a"], "B": ["a"]}, 0),  # good
        ({"A": 1}, {"A": ["a"], "B": ["a"]}, 1),  # extra district
        ({"A": 1, "B": 1}, {"A": ["a"]}, 1),  # missing district
        ({"A": 1, "B": 1}, {"A": [], "B": ["a"]}, 1),  # missing leg
    ],
)
def test_compare_districts(expected, actual, errors):
    e = compare_districts({"upper": expected}, {"upper": actual})
    assert len(e) == errors


def test_compare_districts_overfill():
    expected = {"A": 1}
    actual = {"A": ["Anne", "Bob"]}
    e = compare_districts({"upper": expected}, {"upper": actual})
    assert len(e) == 1
    assert "Anne" in e[0]
    assert "Bob" in e[0]


def test_person_duplicates():
    v = Validator("ak", {}, False, False)

    people = [
        # duplicates across people
        {
            "id": "ocd-person/11111111-1111-1111-1111-111111111111",
            "name": "One",
            "ids": {"twitter": "no-twitter", "youtube": "fake"},
            "roles": [],
        },
        {
            "id": "ocd-person/22222222-2222-2222-2222-222222222222",
            "name": "Two",
            "ids": {"twitter": "no-twitter", "youtube": "fake"},
            "roles": [],
        },
        # duplicate on same person
        {
            "id": "ocd-person/33333333-3333-3333-3333-333333333333",
            "name": "Three",
            "ids": {"twitter": "no-twitter"},
            "other_identifiers": [
                {"scheme": "external_service_id", "identifier": "XYZ"},
                {"scheme": "external_service_id", "identifier": "XYZ"},
            ],
            "roles": [],
        },
        {
            "id": "ocd-person/44444444-4444-4444-4444-444444444444",
            "name": "Four",
            "ids": {"twitter": "no-twitter"},
            "roles": [],
        },
    ]
    for p in people:
        v.validate_person(p, Path(p["name"] + ".yml"), PersonType.LEGISLATIVE)
    errors = v.check_duplicates()
    assert len(errors) == 3
    assert 'duplicate youtube: "fake" One.yml, Two.yml' in errors
    assert 'duplicate external_service_id: "XYZ" Three.yml, Three.yml' in errors
    assert (
        'duplicate twitter: "no-twitter" One.yml, Two.yml, Three.yml and 1 more...'
        in errors
    )


def test_filename_id_test():
    person = dict(
        id=EXAMPLE_OCD_PERSON_ID,
        name="Jane Smith",
        roles=[],
    )
    v = Validator("ak", {}, False, False)
    v.validate_person(person, Path("bad-filename"), PersonType.LEGISLATIVE)
    for err in v.errors["bad-filename"]:
        if "not in filename" in err:
            break
    else:
        raise AssertionError("did not check for id in filename")
