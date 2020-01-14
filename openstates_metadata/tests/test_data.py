from ..data import STATES

def test_basics():
    unicam_count = 0
    bicam_count = 0
    for state in STATES:
        if state.unicameral:
            unicam_count += 1
        else:
            bicam_count += 1
    assert unicam_count == 2
    assert bicam_count == 50

def test_district_numbers():
    for state in STATES:
        if state.unicameral:
            assert state.legislature.num_seats == sum(d.num_seats for d in state.legislature.districts)
        else:
            assert state.upper.num_seats == sum(d.num_seats for d in state.upper.districts)
            assert state.lower.num_seats == sum(d.num_seats for d in state.lower.districts)
