import os
import datetime
from pathlib import Path
import pytest  # type: ignore
from openstates.utils.people.merge import (
    reformat_phone_number,
    reformat_address,
    compute_merge,
    Append,
    Replace,
    merge_people,
    merge_offices,
    find_file,
    collapse_duplicates,
)
from openstates.models.people import OtherName, OtherIdentifier, Office, Party
from pydantic import BaseModel


@pytest.mark.parametrize(
    "input,output",
    [
        ("1234567890", "123-456-7890"),
        ("123-456-7890", "123-456-7890"),
        ("1-123-456-7890", "1-123-456-7890"),
        ("+1-123-456-7890", "1-123-456-7890"),
        ("1-800-FAKENUM", "1-800-FAKENUM"),
        ("email@example.com", "email@example.com"),
        ("555.333.1111", "555-333-1111"),
        ("+1 (555) 333-1111", "1-555-333-1111"),
        ("555-333-1111 ext.100", "555-333-1111 ext. 100"),
        ("555.333.1111 EXT.100", "555-333-1111 ext. 100"),
    ],
)
def test_reformat_phone(input, output):
    assert reformat_phone_number(input) == output


@pytest.mark.parametrize(
    "input,output",
    [
        ("123 Maple Lane\nRaleigh, NC 27511", "123 Maple Lane;Raleigh, NC 27511"),
        (
            "123 Maple Lane   \n   Raleigh, NC    27511",
            "123 Maple Lane;Raleigh, NC 27511",
        ),
        ("123 Maple Lane\n \nRaleigh, NC 27511", "123 Maple Lane;Raleigh, NC 27511"),
    ],
)
def test_reformat_address(input, output):
    assert reformat_address(input) == output


@pytest.mark.parametrize(
    "a, b, output",
    [
        # no diff
        ({"a": "one", "b": "two"}, {"a": "one", "b": "two"}, []),
        # simple difference
        (
            {"a": "one", "b": "two"},
            {"a": "bad", "b": "two"},
            [Replace("a", "one", "bad")],
        ),
        # missing key from first
        ({"a": "one"}, {"a": "one", "b": "two"}, [Replace("b", None, "two")]),
        # missing key from second
        ({"a": "one", "b": "two"}, {"a": "one"}, []),
    ],
)
def test_compute_merge_simple(a, b, output):
    class Model(BaseModel):
        a: str = None
        b: str = None

    assert compute_merge(Model(**a), Model(**b)) == output


@pytest.mark.parametrize(
    "a, b, output",
    [
        # no diff
        ({"a": {"b": "c"}}, {"a": {"b": "c"}}, []),
        # nothing new on right
        ({"a": {"b": "c"}}, {"a": {}}, []),
        # replace
        ({"a": {}}, {"a": {"b": "c"}}, [Replace("a.b", None, "c")]),
    ],
)
def test_compute_merge_nested(a, b, output):
    class Inner(BaseModel):
        b: str = None

    class Model(BaseModel):
        a: Inner = None

    assert compute_merge(Model(**a), Model(**b)) == output


@pytest.mark.parametrize(
    "a, b, output",
    [
        # no errors
        ({"a": [{"b": 1}, {"c": 2}]}, {"a": [{"b": 1}, {"c": 2}]}, []),
        # no errors - just different order
        ({"a": [{"b": 1}, {"c": 2}]}, {"a": [{"c": 2}, {"b": 1}]}, []),
        # extra item left
        ({"a": [{"b": 1}, {"c": 2}, {"d": 3}]}, {"a": [{"b": 1}, {"c": 2}]}, []),
        # extra item right
        (
            {"a": [{"b": 1}, {"c": 2}]},
            {"a": [{"b": 1}, {"c": 2}, {"d": 3}]},
            [Append("a", {"d": 3})],
        ),
    ],
)
def test_compute_merge_list(a, b, output):
    class Model(BaseModel):
        a: list[dict]

    assert compute_merge(Model(**a), Model(**b)) == output


@pytest.mark.parametrize(
    "a, b, keep_both, output",
    [
        # discard id
        ({"id": "1"}, {"id": "2"}, False, []),
        # keep id
        (
            {"id": "1"},
            {"id": "2"},
            True,
            [
                Append(
                    "other_identifiers",
                    OtherIdentifier(identifier="2", scheme="openstates"),
                )
            ],
        ),
        # append name
        (
            {"name": "A"},
            {"name": "B"},
            True,
            [Append("other_names", OtherName(name="A")), Replace("name", "A", "B")],
        ),
    ],
)
def test_compute_merge_special_cases(a, b, keep_both, output):
    class Model(BaseModel):
        id: str = None
        name: str = ""

    assert compute_merge(Model(**a), Model(**b), keep_both_ids=keep_both) == output


def test_compute_merge_party():
    class Model(BaseModel):
        party: list[Party] = []

    # no change
    a = Model(party=[Party(name="Democratic")])
    b = Model(party=[Party(name="Democratic")])
    assert compute_merge(a, b) == []

    # set end date on prior party
    c = Model(party=[Party(name="Republican")])
    today = datetime.date.today().strftime("%Y-%m-%d")
    assert compute_merge(a, c) == [
        Replace(
            "party",
            [
                Party(name="Democratic"),
            ],
            [
                Party(name="Democratic", end_date=today),
                Party(name="Republican"),
            ],
        )
    ]

    # extra data isn't affected
    d = Model(
        party=[
            Party(name="Independent", end_date=today),
            Party(name="Republican"),
        ]
    )
    assert compute_merge(d, c) == []


@pytest.mark.parametrize(
    "old, new, expected",
    [
        # no changes
        ({"name": "Anna"}, {"name": "Anna"}, {"name": "Anna"}),
        # field only in old
        (
            {"name": "Anna", "birth_date": "1980"},
            {"name": "Anna"},
            {"name": "Anna", "birth_date": "1980"},
        ),
        # field only in new
        (
            {"name": "Anna"},
            {"name": "Anna", "birth_date": "1980"},
            {"name": "Anna", "birth_date": "1980"},
        ),
        # special: name field differs
        (
            {"name": "Bob"},
            {"name": "Robert"},
            {"name": "Robert", "other_names": [OtherName(name="Bob")]},
        ),
    ],
)
def test_simple_merge(old, new, expected):
    class Model(BaseModel):
        name: str
        birth_date: str = ""
        other_names: list[OtherName] = []

    assert merge_people(Model(**old), Model(**new)) == Model(**expected)


@pytest.mark.parametrize(
    "old, new, expected",
    [
        # more in first list
        (
            {"other_names": [{"name": "A"}, {"name": "B"}]},
            {"other_names": [{"name": "A"}]},
            {"other_names": [{"name": "A"}, {"name": "B"}]},
        ),
        # more in second list
        (
            {"other_names": [{"name": "A"}]},
            {"other_names": [{"name": "A"}, {"name": "B"}]},
            {"other_names": [{"name": "A"}, {"name": "B"}]},
        ),
        # each list is unique
        (
            {"other_names": [{"name": "A"}]},
            {"other_names": [{"name": "B"}]},
            {"other_names": [{"name": "A"}, {"name": "B"}]},
        ),
    ],
)
def test_list_merge(old, new, expected):
    class Model(BaseModel):
        other_names: list[OtherName] = []

    # note that keep doesn't matter for these
    assert merge_people(Model(**old), Model(**new), None) == Model(**expected)


@pytest.mark.parametrize(
    "old, new, expected",
    [
        # simplest case
        (
            {"id": "ocd-person/1"},
            {"id": "ocd-person/2"},
            {
                "id": "ocd-person/1",
                "other_identifiers": [
                    OtherIdentifier(scheme="openstates", identifier="ocd-person/2")
                ],
            },
        ),
        # already has identifiers
        (
            {
                "id": "ocd-person/1",
                "other_identifiers": [
                    OtherIdentifier(scheme="openstates", identifier="ocd-person/0")
                ],
            },
            {"id": "ocd-person/2"},
            {
                "id": "ocd-person/1",
                "other_identifiers": [
                    OtherIdentifier(scheme="openstates", identifier="ocd-person/0"),
                    OtherIdentifier(scheme="openstates", identifier="ocd-person/2"),
                ],
            },
        ),
    ],
)
def test_keep_both_ids(old, new, expected):
    class Model(BaseModel):
        id: str
        other_identifiers: list[OtherIdentifier] = []

    assert merge_people(Model(**old), Model(**new), keep_both_ids=True) == Model(
        **expected
    )


@pytest.mark.parametrize(
    "old, new",
    [
        (
            [Office(classification="capitol", voice="123-555-9999")],
            [Office(classification="capitol", voice="123-555-9999")],
        ),
        (
            [
                Office(classification="capitol", voice="123-555-9999"),
                Office(classification="district", address="abc"),
            ],
            [
                Office(classification="capitol", voice="123-555-9999"),
                Office(classification="district", address="abc"),
            ],
        ),
    ],
)
def test_merge_office_no_change(old, new):
    assert merge_offices(old, new) is None


@pytest.mark.parametrize(
    "old, new, expected",
    [
        # replace a value with a new one
        (
            [Office(classification="capitol", voice="111-111-1111")],
            [Office(classification="capitol", voice="222-222-2222")],
            [Office(classification="capitol", voice="222-222-2222")],
        ),
        # merge two partial records
        (
            [Office(classification="capitol", voice="111-111-1111")],
            [Office(classification="capitol", fax="444-444-4444")],
            [
                Office(
                    classification="capitol", voice="111-111-1111", fax="444-444-4444"
                )
            ],
        ),
        # merge two offices into a single list
        (
            [Office(classification="capitol", voice="111-111-1111")],
            [Office(classification="district", voice="444-444-4444")],
            [
                Office(classification="capitol", voice="111-111-1111"),
                Office(classification="district", voice="444-444-4444"),
            ],
        ),
    ],
)
def test_merge_offices_changes(old, new, expected):
    assert merge_offices(old, new) == expected


@pytest.mark.parametrize(
    "old, expected",
    [
        # no change
        (
            [
                Office(classification="capitol", voice="222-222-2222"),
                Office(classification="capitol", voice="222-222-2222"),
            ],
            [Office(classification="capitol", voice="222-222-2222")],
        ),
        # one is a subset of the other, return bigger one
        (
            [
                Office(classification="capitol", voice="111-111-1111"),
                Office(
                    classification="capitol", voice="111-111-1111", fax="444-444-4444"
                ),
            ],
            [
                Office(
                    classification="capitol", voice="111-111-1111", fax="444-444-4444"
                )
            ],
        ),
        # only differ by name
        (
            [
                Office(classification="capitol", voice="111-111-1111"),
                Office(
                    classification="capitol",
                    voice="111-111-1111",
                    name="Capitol Office",
                ),
            ],
            [
                Office(
                    classification="capitol",
                    voice="111-111-1111",
                    name="Capitol Office",
                )
            ],
        ),
    ],
)
def test_collapse_duplicates(old, expected):
    assert collapse_duplicates(old) == expected


def test_merge_offices_duplicate():
    old = [Office(classification="district", voice="111-222-3333")]
    new = [
        Office(
            classification="district", voice="111-222-3333", name="District Office #1"
        )
    ]
    assert merge_offices(old, new) == new


def test_merge_extras():
    # replace was adding a key like extras._internal_id
    old = {"extras": {"_internal_id": 123}}
    new = {}
    expected = old.copy()

    class Model(BaseModel):
        extras: dict = {}

    assert merge_people(Model(**new), Model(**old)) == expected


def test_find_file_good():
    os.environ["OS_PEOPLE_DIRECTORY"] = str(Path(__file__).parent / "testdata/people")
    filename = find_file("a2e4a1b2-f0fd-4c35-9e0c-bb009778792f", state="pa")
    assert "Pam-Snyder" in str(filename)
    filename = find_file("a2e4a1b2-f0fd-4c35-9e0c-bb009778792f")
    assert "Pam-Snyder" in str(filename)


def test_find_file_missing():
    with pytest.raises(FileNotFoundError):
        find_file("77777777-ffff-0000-9000-bbbbbbbbbbbb")
    # good file, bad directory
    with pytest.raises(FileNotFoundError):
        find_file("a2e4a1b2-f0fd-4c35-9e0c-bb009778792f", state="nc")
