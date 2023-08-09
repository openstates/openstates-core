# type: ignore
import re

from ..data import STATES_AND_TERRITORIES
from ..data.states import NC, VT


def test_basics() -> None:
    unicam_count = 0
    bicam_count = 0
    for state in STATES_AND_TERRITORIES:
        if state.unicameral:
            unicam_count += 1
            assert state.legislature
            assert not state.lower
            assert not state.upper
        else:
            bicam_count += 1
            assert not state.legislature
            assert state.lower
            assert state.upper
    assert unicam_count == 4
    assert bicam_count == 52


def test_district_numbers() -> None:
    for state in STATES_AND_TERRITORIES:
        if state.unicameral:
            assert state.legislature.num_seats == sum(
                d.num_seats for d in state.legislature.districts
            )
            assert state.legislature.num_seats > 0
        else:
            assert state.upper.num_seats == sum(
                d.num_seats for d in state.upper.districts
            )
            assert state.lower.num_seats == sum(
                d.num_seats for d in state.lower.districts
            )
            assert state.lower.num_seats > state.upper.num_seats > 8


def test_simple_numbered_districts() -> None:
    assert NC.lower.districts[0].name == "1"
    assert NC.lower.districts[0].num_seats == 1
    assert NC.lower.districts[-1].name == "120"
    assert NC.lower.districts[0].num_seats == 1


def test_everything_has_division_id() -> None:
    for state in STATES_AND_TERRITORIES:
        if state.unicameral:
            for d in state.legislature.districts:
                assert d.num_seats
                assert d.division_id.startswith(state.division_id)
        elif state.abbr == "US":
            for d in state.lower.districts:
                assert d.num_seats == 1
                assert re.match(
                    r"ocd-division/country:us/(district:dc|territory:(pr|as|mp|gu|vi)|state:\w\w/cd:)",
                    d.division_id,
                )
            for d in state.upper.districts:
                assert d.num_seats == 2
                assert re.match(r"ocd-division/country:us/state:\w\w$", d.division_id)
        else:
            for d in state.lower.districts:
                assert d.num_seats
                assert d.division_id.startswith(f"{state.division_id}/sldl:")
            for d in state.upper.districts:
                assert d.num_seats
                if d.name == "At-Large":
                    assert d.division_id == state.division_id
                else:
                    assert d.division_id.startswith(f"{state.division_id}/sldu:")


def test_everything_has_organization_id() -> None:
    for state in STATES_AND_TERRITORIES:
        if state.unicameral:
            assert len(state.legislature.organization_id) == 53
        else:
            assert len(state.lower.organization_id) == 53
            assert len(state.upper.organization_id) == 53


def test_legacy_ids() -> None:
    assert not NC.legacy_districts
    assert len(VT.legacy_districts) == 88
