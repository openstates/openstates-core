import os
import json
import shutil
import tempfile
import datetime
import pytest
from unittest import mock
from openstates.data.models import (
    Bill,
    Jurisdiction,
    Division,
    LegislativeSession,
    Organization,
    Person,
)
from openstates.scrape import Bill as ScrapeBill
from openstates.importers.base import omnihash, BaseImporter
from openstates.importers import BillImporter
from openstates.exceptions import UnresolvedIdError, DataImportError


def create_jurisdiction():
    Division.objects.create(id="ocd-division/country:us", name="USA")
    j = Jurisdiction.objects.create(id="jid", division_id="ocd-division/country:us")
    Organization.objects.create(jurisdiction_id="jid", classification="legislature")
    LegislativeSession.objects.create(
        jurisdiction_id="jid", name="2020", identifier="2020"
    )
    return j


class FakeImporter(BaseImporter):
    _type = "test"


def test_omnihash_python_types():
    # string
    assert omnihash("test") == omnihash("test")
    # list
    assert omnihash(["this", "is", "a", "list"]) == omnihash(
        ["this", "is", "a", "list"]
    )
    # set
    assert omnihash({"and", "a", "set"}) == omnihash({"set", "set", "and", "a"})
    # dict w/ set and tuple as well
    assert omnihash({"a": {("fancy", "nested"): {"dict"}}}) == omnihash(
        {"a": {("fancy", "nested"): {"dict"}}}
    )


def test_import_directory():
    # write out some temp data to filesystem
    datadir = tempfile.mkdtemp()
    dicta = {"test": "A"}
    dictb = {"test": "B"}
    open(os.path.join(datadir, "test_a.json"), "w").write(json.dumps(dicta))
    open(os.path.join(datadir, "test_b.json"), "w").write(json.dumps(dictb))

    # simply ensure that import directory calls import_data with all dicts
    ti = FakeImporter("jurisdiction-id")
    with mock.patch.object(ti, attribute="import_data") as mockobj:
        ti.import_directory(datadir)

    # import_data should be called once
    assert mockobj.call_count == 1
    # kind of hacky, get the total list of args passed in
    arg_objs = list(mockobj.call_args[0][0])

    # 2 args only, make sure a and b are in there
    assert len(arg_objs) == 2
    assert dicta in arg_objs
    assert dictb in arg_objs

    # clean up datadir
    shutil.rmtree(datadir)


def test_apply_transformers():
    transformers = {
        "capitalize": lambda x: x.upper(),
        "cap_and_reverse": [lambda x: x.upper(), lambda y: y[::-1]],
        "never_used": lambda x: 1 / 0,
        "nested": {"replace": lambda x: "replaced"},
    }
    data = {
        "capitalize": "words",
        "cap_and_reverse": "simple",
        "nested": {"replace": None},
    }
    ti = FakeImporter("jid")
    ti.cached_transformers = transformers
    output = ti.apply_transformers(data)
    assert output["capitalize"] == "WORDS"
    assert output["cap_and_reverse"] == "ELPMIS"
    assert output["nested"]["replace"] == "replaced"


# doing these next few tests just on a Bill because it is the same code that handles it
# but for completeness maybe it is better to do these on each type?


@pytest.mark.django_db
def test_deduplication_identical_object():
    create_jurisdiction()
    p1 = ScrapeBill("HB 1", "2020", "Title").as_dict()
    p2 = ScrapeBill("HB 1", "2020", "Title").as_dict()
    BillImporter("jid").import_data([p1, p2])

    assert Bill.objects.count() == 1


@pytest.mark.django_db
def test_exception_on_identical_objects_in_import_stream():
    create_jurisdiction()
    # the first two objects aren't identical, but refer to the same thing
    # at the moment we drop both objects (because we can't know which one is correct)
    b1 = ScrapeBill("HB 1", "2020", "Title", chamber="upper").as_dict()
    b2 = ScrapeBill("HB 1", "2020", "Title", chamber="lower").as_dict()
    b3 = ScrapeBill("HB 2", "2020", "Bill Title").as_dict()

    BillImporter("jid").import_data([b1, b2, b3])
    assert Bill.objects.count() == 1


@pytest.mark.django_db
def test_resolve_json_id():
    create_jurisdiction()
    p1 = ScrapeBill("HB 1", "2020", "Title").as_dict()
    p2 = ScrapeBill("HB 1", "2020", "Title").as_dict()
    bi = BillImporter("jid")

    # do import and get database id
    p1_id = p1["_id"]
    p2_id = p2["_id"]
    bi.import_data([p1, p2])
    db_id = Bill.objects.get().id

    # simplest case
    assert bi.resolve_json_id(p1_id) == db_id
    # duplicate should resolve to same id
    assert bi.resolve_json_id(p2_id) == db_id
    # a null id should map to None
    assert bi.resolve_json_id(None) is None
    # no such id
    with pytest.raises(UnresolvedIdError):
        bi.resolve_json_id("this-is-invalid")


@pytest.mark.django_db
def test_invalid_fields():
    create_jurisdiction()
    p1 = ScrapeBill("HB 1", "2020", "Title").as_dict()
    p1["newfield"] = "shouldn't happen"

    with pytest.raises(DataImportError):
        BillImporter("jid").import_data([p1])


@pytest.mark.django_db
def test_invalid_fields_related_item():
    create_jurisdiction()
    p1 = ScrapeBill("HB 1", "2020", "Title")
    p1.add_source("http://example.com")
    p1 = p1.as_dict()
    p1["sources"][0]["test"] = 3

    with pytest.raises(DataImportError):
        BillImporter("jid").import_data([p1])


@pytest.mark.django_db
def test_automatic_updated_at():
    create_jurisdiction()
    difference = Organization.objects.get().updated_at - datetime.datetime.utcnow()
    # updated_at should be in UTC, a bit of clock drift notwithstanding
    assert abs(difference) < datetime.timedelta(minutes=5)


@pytest.mark.django_db
def test_resolve_person_normal():
    create_jurisdiction()
    bi = BillImporter("jid")
    org = Organization.objects.get(jurisdiction_id="jid", classification="legislature")
    p = Person.objects.create(name="John McGuirk")
    p.memberships.create(organization=org)

    assert bi.resolve_person('~{"name": "John McGuirk"}') == p.id


@pytest.mark.django_db
def test_resolve_person_case_insensitive():
    create_jurisdiction()
    bi = BillImporter("jid")
    org = Organization.objects.get(jurisdiction_id="jid", classification="legislature")
    p = Person.objects.create(name="John McGuirk")
    p.memberships.create(organization=org)

    assert bi.resolve_person('~{"name": "JohN mCgUIrk"}') == p.id


@pytest.mark.django_db
def test_resolve_person_cache_key_includes_org_classification():
    """resolve_person()'s cache used to key only on (psuedo_person_id,
    start_date, end_date) -- omitting org_classification. Two same-surname
    people in different chambers of the same jurisdiction, looked up with the
    SAME session dates (the normal case -- a jurisdiction's chambers usually
    share one LegislativeSession), produced the SAME cache key despite being
    genuinely different queries. Whichever chamber got resolved first within
    an import run silently poisoned the cache for the other for the rest of
    that run."""
    create_jurisdiction()
    upper_org = Organization.objects.create(jurisdiction_id="jid", classification="upper")
    lower_org = Organization.objects.create(jurisdiction_id="jid", classification="lower")
    upper_person = Person.objects.create(name="Smith")
    upper_person.memberships.create(organization=upper_org)
    lower_person = Person.objects.create(name="Smith")
    lower_person.memberships.create(organization=lower_org)

    bi = BillImporter("jid")
    same_start, same_end = "2026-01-01", "2026-12-31"

    resolved_upper = bi.resolve_person(
        '~{"name": "Smith"}', same_start, same_end, "upper"
    )
    resolved_lower = bi.resolve_person(
        '~{"name": "Smith"}', same_start, same_end, "lower"
    )

    assert resolved_upper == upper_person.id
    assert resolved_lower == lower_person.id, (
        "The lower-chamber lookup must resolve its own chamber's person, not "
        "reuse the upper-chamber lookup's cached result just because the "
        "name and session dates are identical."
    )


@pytest.mark.django_db
def test_resolve_person_cache_key_includes_org_classification_reverse_order():
    """Same shape as above, chambers queried in the opposite order -- the bug
    doesn't care which chamber is resolved first, so neither should the fix."""
    create_jurisdiction()
    upper_org = Organization.objects.create(jurisdiction_id="jid", classification="upper")
    lower_org = Organization.objects.create(jurisdiction_id="jid", classification="lower")
    upper_person = Person.objects.create(name="Smith")
    upper_person.memberships.create(organization=upper_org)
    lower_person = Person.objects.create(name="Smith")
    lower_person.memberships.create(organization=lower_org)

    bi = BillImporter("jid")
    same_start, same_end = "2026-01-01", "2026-12-31"

    resolved_lower = bi.resolve_person(
        '~{"name": "Smith"}', same_start, same_end, "lower"
    )
    resolved_upper = bi.resolve_person(
        '~{"name": "Smith"}', same_start, same_end, "upper"
    )

    assert resolved_lower == lower_person.id
    assert resolved_upper == upper_person.id


@pytest.mark.django_db
def test_resolve_person_cache_key_includes_embedded_chamber():
    """The cache key is built AFTER a chamber embedded in psuedo_person_id
    (rather than passed as the explicit org_classification argument, e.g. the
    bill-sponsorship lookup path) is folded in -- covers that path
    specifically. Two embedded chambers must not collide just because the
    caller never passed org_classification explicitly."""
    create_jurisdiction()
    upper_org = Organization.objects.create(jurisdiction_id="jid", classification="upper")
    lower_org = Organization.objects.create(jurisdiction_id="jid", classification="lower")
    upper_person = Person.objects.create(name="Smith")
    upper_person.memberships.create(organization=upper_org)
    lower_person = Person.objects.create(name="Smith")
    lower_person.memberships.create(organization=lower_org)

    bi = BillImporter("jid")
    same_start, same_end = "2026-01-01", "2026-12-31"

    resolved_upper = bi.resolve_person(
        '~{"name": "Smith", "chamber": "upper"}', same_start, same_end
    )
    resolved_lower = bi.resolve_person(
        '~{"name": "Smith", "chamber": "lower"}', same_start, same_end
    )

    assert resolved_upper == upper_person.id
    assert resolved_lower == lower_person.id, (
        "A chamber embedded in psuedo_person_id must participate in the "
        "cache key the same way an explicit org_classification does."
    )


@pytest.mark.django_db
def test_resolve_person_same_chamber_still_hits_cache():
    """The fix must not turn the cache into a no-op -- a second lookup with
    the SAME org_classification (the common case: many votes on one bill, one
    chamber) should still be served from cache, not re-query every time."""
    create_jurisdiction()
    org = Organization.objects.create(jurisdiction_id="jid", classification="lower")
    person = Person.objects.create(name="Smith")
    person.memberships.create(organization=org)

    bi = BillImporter("jid")
    first = bi.resolve_person('~{"name": "Smith"}', "2026-01-01", "2026-12-31", "lower")
    cache_size_after_first = len(bi.person_cache)
    second = bi.resolve_person('~{"name": "Smith"}', "2026-01-01", "2026-12-31", "lower")

    assert first == person.id
    assert second == person.id
    assert len(bi.person_cache) == cache_size_after_first, (
        "A repeat lookup with the same org_classification must hit the "
        "existing cache entry, not add a new one."
    )


@pytest.mark.django_db
def test_resolve_bill_by_date():
    j = create_jurisdiction()
    session = j.legislative_sessions.create(
        name="2021",
        identifier="2021",
        start_date="2021-01-01",
        end_date="2021-12-31",
    )
    bi = BillImporter("jid")
    b = Bill.objects.create(
        identifier="HB 1", title="Some Bill", legislative_session=session
    )

    assert bi.resolve_bill("HB 1", date="2021-05-06") == b.id


@pytest.mark.django_db
def test_resolve_bill_by_date_transformers():
    j = create_jurisdiction()
    session = j.legislative_sessions.create(
        name="2021",
        identifier="2021",
        start_date="2021-01-01",
        end_date="2021-12-31",
    )
    bi = BillImporter("jid")
    b = Bill.objects.create(
        identifier="HB 1", title="Some Bill", legislative_session=session
    )
    assert bi.resolve_bill("hb1", date="2021-05-06") == b.id


@pytest.mark.django_db
def test_resolve_bill_by_date_open_session():
    j = create_jurisdiction()
    session = j.legislative_sessions.create(
        name="2021",
        identifier="2021",
        start_date="2021-01-01",
        # no end date
    )
    bi = BillImporter("jid")
    b = Bill.objects.create(
        identifier="HB 1", title="Some Bill", legislative_session=session
    )

    assert bi.resolve_bill("HB 1", date="2021-05-06") == b.id
