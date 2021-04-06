import pytest
from openstates.utils.transformers import fix_bill_id


@pytest.mark.parametrize(
    "orig,exp",
    [
        ("HB1", "HB 1"),
        ("   HB1  ", "HB 1"),
        ("HB 0001", "HB 1"),
        ("hb    1", "HB 1"),
        ("SJRA", "SJR A"),
    ],
)
def test_fix_bill_id(orig, exp):
    assert fix_bill_id(orig) == exp
