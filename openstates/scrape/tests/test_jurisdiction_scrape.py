from collections import defaultdict
from openstates.scrape import State, Organization, JurisdictionScraper
from openstates.exceptions import ScrapeValueError
import pytest


class NewJersey(State):
    pass


def test_basics():
    # id property and string
    j = NewJersey()
    assert j.jurisdiction_id == "ocd-jurisdiction/country:us/state:nj/government"
    assert j.name in str(j)


def test_as_dict():
    j = NewJersey()
    d = j.as_dict()

    assert d["_id"] == j.jurisdiction_id
    assert d["name"] == j.name
    assert d["url"] == j.url
    assert d["legislative_sessions"] == []


def test_jurisdiction_unicam_scrape():
    class Nebraska(State):
        pass

    j = Nebraska()
    js = JurisdictionScraper(j, "/tmp/")
    objects = list(js.scrape())

    # two objects, first is the Jurisdiction
    assert len(objects) == 2
    assert objects[0] == j

    # ensure we made a single legislature org
    assert isinstance(objects[1], Organization)
    assert objects[1].classification == "legislature"


def test_jurisdiction_bicameral_scrape():
    j = NewJersey()
    js = JurisdictionScraper(j, "/tmp/")
    objects = list(js.scrape())
    obj_names = set()
    obj_types = defaultdict(int)

    for o in objects:
        obj_names.add(o.name)
        obj_types[type(o)] += 1

    # ensure Jurisdiction and 3 organizations were found
    assert obj_names == {"New jersey Legislature", "Assembly", "New Jersey", "Senate"}
    assert obj_types[NewJersey] == 1
    assert obj_types[Organization] == 3


def test_jurisdiction_validate_sessions():
    j = NewJersey()
    j.legislative_sessions = [
        {
            "_scraped_name": "s1",
            "classification": "primary",
            "name": "First Session",
            "start_date": "2020-01-01",
        }
    ]
    with pytest.raises(ScrapeValueError):
        j.validate()
    j.legislative_sessions[0]["end_date"] = "2020-02-01"
    j.validate()
