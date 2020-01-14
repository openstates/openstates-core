from ..data import STATES, NC


def test_basics():
    unicam_count = 0
    bicam_count = 0
    for state in STATES:
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
    assert unicam_count == 2
    assert bicam_count == 50


def test_district_numbers():
    for state in STATES:
        if state.unicameral:
            assert state.legislature.num_seats == sum(
                d.num_seats for d in state.legislature.districts
            )
        else:
            assert state.upper.num_seats == sum(
                d.num_seats for d in state.upper.districts
            )
            assert state.lower.num_seats == sum(
                d.num_seats for d in state.lower.districts
            )


def test_simple_numbered_districts():
    assert NC.lower.districts[0].name == "1"
    assert NC.lower.districts[0].num_seats == 1
