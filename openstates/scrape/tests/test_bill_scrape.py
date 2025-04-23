import pytest
import warnings
from datetime import date
from openstates.scrape import Bill, State
from openstates.utils.generic import get_pseudo_id
from openstates.exceptions import ScrapeValueError


class NewJersey(State):
    pass


def toy_bill():
    b = Bill(
        identifier="HB 2017",
        legislative_session="2012A",
        title="A bill for an act to raise the cookie budget by 200%",
        from_organization="Foo Senate",
        classification="bill",
    )
    b.add_source("http://uri.example.com/", note="foo")
    return b


def test_basic_valid_bill():
    b = toy_bill()
    b.validate()
    assert "we got here"


def test_bill_type_setting():
    # default
    b = Bill(identifier="some bill", legislative_session="session", title="the title")
    assert b.classification == ["bill"]

    # string -> list
    b = Bill(
        identifier="some bill",
        legislative_session="session",
        title="the title",
        classification="string",
    )
    assert b.classification == ["string"]

    # list unmodified
    b = Bill(
        identifier="some bill",
        legislative_session="session",
        title="the title",
        classification=["two", "items"],
    )
    # will be sorted
    assert b.classification == ["items", "two"]

    # tuple -> list
    b = Bill(
        identifier="some bill",
        legislative_session="session",
        title="the title",
        classification=("two", "items"),
    )
    assert b.classification == ["items", "two"]


def test_basic_invalid_bill():
    """ Test that we can create an invalid bill, and validation will fail """
    b = toy_bill()
    b.identifier = None
    with pytest.raises(ValueError):
        b.validate()


def test_from_organization():
    # none set
    assert get_pseudo_id(Bill("HB 1", "2014", "Some Bill").from_organization) == {
        "classification": "legislature"
    }

    # chamber set
    assert get_pseudo_id(
        Bill("SB 1", "2014", "Some Bill", chamber="upper").from_organization
    ) == {"classification": "upper"}
    # org direct set
    assert (
        Bill("HB 1", "2014", "Some Bill", from_organization="test").from_organization
        == "test"
    )

    # can't set both
    with pytest.raises(ValueError):
        Bill("HB 1", "2014", "Some Bill", from_organization="upper", chamber="upper")


def test_add_action():
    """ Make sure actions work """
    b = toy_bill()
    b.add_action("Some dude liked it.", "2013-04-29T20:00Z", chamber="lower")
    assert len(b.actions) == 1
    assert b.actions[0]["description"] == "Some dude liked it."
    assert get_pseudo_id(b.actions[0]["organization_id"]) == {"classification": "lower"}
    assert b.actions[0]["date"] == "2013-04-29T20:00Z"
    b.validate()


def test_add_related_bill():
    """ Make sure related bills work """
    b = toy_bill()
    b.add_related_bill(
        identifier="HB 2020", legislative_session="2011A", relation_type="companion"
    )
    assert len(b.related_bills) == 1
    assert b.related_bills[0] == {
        "identifier": "HB 2020",
        "legislative_session": "2011A",
        "relation_type": "companion",
    }
    b.validate()


def test_add_sponsor():
    b = toy_bill()
    b.add_sponsorship(
        name="Joe Bleu",
        classification="Author",
        entity_type="person",
        primary=True,
        chamber="upper",
    )
    assert len(b.sponsorships) == 1
    assert b.sponsorships[0] == {
        "person_id": '~{"chamber": "upper", "name": "Joe Bleu"}',
        "name": "Joe Bleu",
        "classification": "Author",
        "entity_type": "person",
        "primary": True,
        "organization_id": None,
    }
    b.validate()


def test_subjects():
    b = toy_bill()
    b.add_subject("Foo")
    b.add_subject("Bar")
    assert b.subject == ["Foo", "Bar"]
    b.validate()


def test_abstract():
    b = toy_bill()
    b.add_abstract("this bill is stupid", "K-5")
    b.add_abstract("this legislative document is ignorant", "6-12")
    assert b.abstracts == [
        {"note": "K-5", "abstract": "this bill is stupid"},
        {"note": "6-12", "abstract": "this legislative document is ignorant"},
    ]


def test_add_documents():
    b = toy_bill()

    # should only add one document since they all have same note
    b.add_document_link(
        note="Fiscal Impact",
        date="2013-04",
        url="http://hi.example.com/foo#bar",
        media_type="text/html",
    )
    b.add_document_link(note="Fiscal Impact", date="2013-04", url="http://foobar.baz")
    assert len(b.documents) == 1

    # should now be two documents
    b.add_document_link(
        note="Other Document", date="2013-04", url="http://foobar.baz/other"
    )
    assert len(b.documents) == 2

    # valid documents so far
    b.validate()

    # an invalid document
    b.add_document_link(
        note="Fiscal Impact", date="2013-04", url=None, media_type="foo"
    )
    with pytest.raises(ScrapeValueError):
        b.validate()


def test_citations():
    b = toy_bill()

    b.add_citation(
        "Wyoming Chapter Laws of 2019",
        "CH0024",
        citation_type="chapter",
        effective=date(2019, 7, 1)
    )

    b.add_citation(
        "Minnesota Session Laws, 2020",
        "Chapter 89",
        citation_type="chapter",
        effective=date(2020, 8, 1),
        url="https://www.revisor.mn.gov/laws/2020/0/Session+Law/Chapter/89/",
    )

    b.add_citation(
        "DC Register",
        "Vol 67 and Page 14429",
        citation_type="final",
        expires="2021-03-06"
    )

    b.add_citation(
        "Constitution of Missouri",
        "Article X Section 6",
        citation_type="proposed",
    )

    b.validate()
    assert len(b.citations) == 4

    with pytest.raises(TypeError):
        # Missing citation
        b.add_citation(
            "Legal Code of Elbonia",
            url="http://openstates.org",
        )

        # Invalid citation
        b.add_citation(
            "Legal Code of Elbonia",
            "",
            citation_type="final",
        )

        # invalid citation type
        b.add_citation(
            "Legal Code of Elbonia",
            "Chapter 12",
            citation_type="aspiration",
        )

        b.validate()


def test_versions():
    b = toy_bill()

    # only one document, multiple links
    b.add_version_link(
        url="http://pault.ag/",
        note="Final Version",
        date="2013-04",
        on_duplicate="error",
        classification="filed",
    )
    b.add_version_link(
        url="http://pault.ag/foo",
        note="Final Version",
        date="2013-04",
        on_duplicate="error",
        classification="filed",
    )
    b.validate()
    assert len(b.versions) == 1
    assert len(b.versions[0]["links"]) == 2

    # duplicate!
    with pytest.raises(ValueError):
        b.add_version_link(
            url="http://pault.ag/foo",
            note="Final Version",
            date="2013-04",
            on_duplicate="error",
        )

    # ignore duplicate - nothing should change
    b.add_version_link(
        url="http://pault.ag/foo",
        note="Final Version",
        date="2013-04",
        classification="filed",
        on_duplicate="ignore",
    )
    assert len(b.versions) == 1
    assert len(b.versions[0]["links"]) == 2

    # duplicate URL
    with pytest.raises(ValueError):
        b.add_version_link(
            url="http://pault.ag/foo",
            note="Finals Versions",
            date="2013-04",
            on_duplicate="error",
        )
    assert len(b.versions) == 1
    assert len(b.versions[0]["links"]) == 2

    # a new doc, numbers go up
    b.add_version_link(
        url="http://pault.ag/foovbar", note="Finals Versions", date="2013-04"
    )
    assert len(b.versions) == 2
    assert len(b.versions[1]["links"]) == 1

    # still validates
    b.validate()


def test_str():
    b = toy_bill()
    assert b.identifier in str(b)


def test_pre_save():
    b = toy_bill()
    j = NewJersey()
    b.add_subject("ZZZ")
    b.add_subject("AAA")
    b.add_subject("MMM")
    b.pre_save(j)
    assert b.subject == ["AAA", "MMM", "ZZZ"]


def test_duplicate_sponsor_warning():
    b = toy_bill()
    b.add_sponsorship(
        name="Joe Bleu",
        classification="Author",
        entity_type="person",
        primary=True,
        chamber="upper",
    )
    with warnings.catch_warnings(record=True) as w:
        b.add_sponsorship(
            name="Joe Bleu",
            classification="Author",
            entity_type="person",
            primary=True,
            chamber="upper",
        )
        assert len(w) == 1
        assert "duplicate sponsor" in str(w[0].message)
