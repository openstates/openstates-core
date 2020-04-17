from .. import lookup
from ..data import NC, NE


def test_lookup():
    assert lookup(abbr="nc") == NC
    assert lookup(abbr="NC") == NC
    assert (
        lookup(jurisdiction_id="ocd-jurisdiction/country:us/state:nc/government") == NC
    )


def test_chambers():
    assert len(NC.chambers) == 2
    assert len(NE.chambers) == 1


def test_lookup_district():
    # lookup works
    assert NC.lookup_district("ocd-division/country:us/state:nc/sldl:1") is not None
    assert NC.lookup_district("ocd-division/country:us/state:nc/sldl:1").name == "1"
    # correct chambers
    assert (
        NC.lookup_district("ocd-division/country:us/state:nc/sldl:1").chamber_type
        == "lower"
    )
    assert (
        NC.lookup_district("ocd-division/country:us/state:nc/sldu:1").chamber_type
        == "upper"
    )
    # unicameral
    assert (
        NE.lookup_district("ocd-division/country:us/state:ne/sldu:1").chamber_type
        == "legislature"
    )


def test_lookup_missing():
    assert NE.lookup_district("ocd-division/country:us/state:ne/sldl:1") is None
