import pytest
from unittest import mock
from openstates.scrape import Bill, State, EmptyScrape
from openstates.scrape.base import Scraper, ScrapeError, BaseBillScraper


class NewJersey(State):
    pass


juris = NewJersey()


def test_save_object_basics():
    # ensure that save object dumps a file
    s = Scraper(juris, "/tmp/")
    p = Bill("HB 1", "2021", "Test")
    p.add_source("http://example.com")

    with mock.patch("json.dump") as json_dump:
        s.save_object(p)

    # ensure object is saved in right place
    filename = "bill_" + p._id + ".json"
    assert filename in s.output_names["bill"]
    json_dump.assert_called_once_with(p.as_dict(), mock.ANY, cls=mock.ANY)


def test_save_object_invalid():
    s = Scraper(juris, "/tmp/")
    p = Bill("HB 1", "2021", "Test")
    # no source, won't validate

    with pytest.raises(ValueError):
        s.save_object(p)


def test_save_related():
    s = Scraper(juris, "/tmp/")
    p = Bill("HB 1", "2021", "Test")
    p.add_source("http://example.com")
    o = Bill("HB 2", "2021", "Test")
    o.add_source("http://example.com")
    p._related.append(o)

    with mock.patch("json.dump") as json_dump:
        s.save_object(p)

    assert json_dump.mock_calls == [
        mock.call(p.as_dict(), mock.ANY, cls=mock.ANY),
        mock.call(o.as_dict(), mock.ANY, cls=mock.ANY),
    ]


def test_simple_scrape():
    class FakeScraper(Scraper):
        def scrape(self):
            p = Bill("HB 1", "2021", "Test")
            p.add_source("http://example.com")
            yield p

    with mock.patch("json.dump") as json_dump:
        record = FakeScraper(juris, "/tmp/").do_scrape()

    assert len(json_dump.mock_calls) == 1
    assert record["objects"]["bill"] == 1
    assert record["end"] > record["start"]
    assert record["skipped"] == 0


def test_double_iter():
    """ tests that scrapers that yield iterables work OK """

    class IterScraper(Scraper):
        def scrape(self):
            yield self.scrape_people()

        def scrape_people(self):
            p = Bill("HB 1", "2021", "The Club")
            p.add_source("http://example.com")
            yield p

    with mock.patch("json.dump") as json_dump:
        record = IterScraper(juris, "/tmp/").do_scrape()

    assert len(json_dump.mock_calls) == 1
    assert record["objects"]["bill"] == 1


def test_no_objects():
    class NullScraper(Scraper):
        def scrape(self):
            pass

    with pytest.raises(ScrapeError):
        NullScraper(juris, "/tmp/", fastmode=True).do_scrape()


def test_no_objects_empty_scrape():
    class NullScraper(Scraper):
        def scrape(self):
            raise EmptyScrape()

    # doesn't raise despite yielding zero objects
    NullScraper(juris, "/tmp/", fastmode=True).do_scrape()


def test_empty_scrape_with_objects():
    class TestScraper(Scraper):
        def scrape(self):
            p = Bill("HB 6", "2021", "Don Jaggerty")
            p.add_source("https://example.com")
            yield p
            raise EmptyScrape()

    # can't yield objects and raise EmptyScrape
    with pytest.raises(ScrapeError):
        TestScraper(juris, "/tmp/", fastmode=True).do_scrape()


def test_no_scrape():
    class NonScraper(Scraper):
        pass

    with pytest.raises(NotImplementedError):
        NonScraper(juris, "/tmp/").do_scrape()


def test_bill_scraper():
    class BillScraper(BaseBillScraper):
        def get_bill_ids(self):
            yield "1", {"extra": "param"}
            yield "2", {}

        def get_bill(self, bill_id, **kwargs):
            if bill_id == "1":
                assert kwargs == {"extra": "param"}
                raise self.ContinueScraping
            else:
                assert bill_id == "2"
                assert kwargs == {}
                b = Bill("1", self.legislative_session, "title")
                b.add_source("http://example.com")
                return b

    bs = BillScraper(juris, "/tmp/")
    with mock.patch("json.dump") as json_dump:
        record = bs.do_scrape(legislative_session="2020")

    assert len(json_dump.mock_calls) == 1
    assert record["objects"]["bill"] == 1
    assert record["skipped"] == 1


def test_whitespace_is_stripped():
    s = Scraper(juris, "/tmp/")
    b = Bill(" HB 11", "2020", " a short title     ")
    b.subject = [" one", "two ", "   three "]
    b.add_source("https://example.com/     ")

    s.save_object(b)

    # the simple cases, and nested lists / objects
    assert b.identifier == "HB 11"
    assert b.title == "a short title"
    assert b.sources[0]["url"] == "https://example.com/"
    # subject got sorted by pre_save
    assert b.subject == ["one", "three", "two"]
