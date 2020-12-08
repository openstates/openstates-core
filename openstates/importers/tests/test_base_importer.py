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
)
from openstates.scrape import Bill as ScrapeBill
from openstates.importers.base import omnihash, BaseImporter
from openstates.importers import BillImporter
from openstates.exceptions import UnresolvedIdError, DataImportError


def create_jurisdiction():
    Division.objects.create(id="ocd-division/country:us", name="USA")
    Jurisdiction.objects.create(id="jid", division_id="ocd-division/country:us")
    Organization.objects.create(jurisdiction_id="jid", classification="legislature")
    LegislativeSession.objects.create(
        jurisdiction_id="jid", name="2020", identifier="2020"
    )


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
    # these two objects aren't identical, but refer to the same thing
    # at the moment we consider this an error (but there may be a better way to handle this?)
    b1 = ScrapeBill("HB 1", "2020", "Title", chamber="upper").as_dict()
    b2 = ScrapeBill("HB 1", "2020", "Title", chamber="lower").as_dict()

    with pytest.raises(Exception):
        BillImporter("jid").import_data([b1, b2])


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
