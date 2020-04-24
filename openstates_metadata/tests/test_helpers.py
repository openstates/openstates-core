import pytest
from .. import lookup, lookup_district_with_ancestors
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


def test_lookup_district_by_division_id():
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


def test_lookup_district_by_name():
    assert (
        NC.lookup_district(chamber="upper", name="1").division_id
        == "ocd-division/country:us/state:nc/sldu:1"
    )
    assert (
        NC.lookup_district(chamber="lower", name="1").division_id
        == "ocd-division/country:us/state:nc/sldl:1"
    )
    assert (
        NE.lookup_district(name="1").division_id
        == "ocd-division/country:us/state:ne/sldu:1"
    )


def test_lookup_missing_district():
    assert NE.lookup_district("ocd-division/country:us/state:ne/sldl:1") is None
    assert NE.lookup_district(name="999") is None
    assert NC.lookup_district(name="999") is None
    assert NC.lookup_district(name="999", chamber="lower") is None


def test_lookup_district_with_ancestors():
    state, chamber, district = lookup_district_with_ancestors(
        division_id="ocd-division/country:us/state:nc/sldl:1"
    )
    assert state.name == "North Carolina"
    assert chamber.chamber_type == "lower"
    assert district.name == "1"

    state, chamber, district = lookup_district_with_ancestors(
        division_id="ocd-division/country:us/state:ne/sldu:1"
    )
    assert state.name == "Nebraska"
    assert chamber.chamber_type == "unicameral"
    assert district.name == "1"


def test_lookup_district_with_ancestors_invalid():
    # bad id
    with pytest.raises(ValueError):
        lookup_district_with_ancestors(division_id="invalid id")
    # bad state
    with pytest.raises(ValueError):
        lookup_district_with_ancestors(
            division_id="ocd-division/country:us/state:xy/sldl:1"
        )
    # bad district
    with pytest.raises(ValueError):
        lookup_district_with_ancestors(
            division_id="ocd-division/country:us/state:nc/sldl:999"
        )


def test_lookup_district_with_ancestors_dc_pr():
    state, chamber, district = lookup_district_with_ancestors(
        division_id="ocd-division/country:us/district:dc"
    )
    assert state.name == "District of Columbia"
    assert chamber.chamber_type == "unicameral"
    assert district.name == "At-Large"
    state, chamber, district = lookup_district_with_ancestors(
        division_id="ocd-division/country:us/territory:pr"
    )
    assert state.name == "Puerto Rico"
    assert chamber.chamber_type == "upper"
    assert district.name == "At-Large"
