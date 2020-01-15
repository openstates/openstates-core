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
