import pytest  # type: ignore
from openstates.utils.transformers import fix_bill_id, collapse_whitespace


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
def test_fix_bill_id(orig: str, exp: str) -> None:
    assert fix_bill_id(orig) == exp


@pytest.mark.parametrize(
    "orig,exp",
    [
        ("HR 1", "HR 1"),
        ("HJRES 1", "HJRES 1"),
        ("HCONRES 1", "HCONRES 1"),
        ("HRES 1", "HRES 1"),
        ("S 1", "S 1"),
        ("SJRES 1", "SJRES 1"),
        ("SCONRES 1", "SCONRES 1"),
        ("SRES 1", "SRES 1"),
    ],
)
def test_fix_bill_id_federal(orig: str, exp: str) -> None:
    assert fix_bill_id(orig) == exp


@pytest.mark.parametrize(
    "orig,exp",
    [
        ("Simple", "Simple"),
        ("One Space", "One Space"),
        ("Two  Spaces", "Two Spaces"),
        ("Line\nBreak", "Line Break"),
        ("Many  Breaks \rto  \t  Fix", "Many Breaks to Fix"),
    ],
)
def test_collapse_whitespace(orig: str, exp: str) -> None:
    assert collapse_whitespace(orig) == exp
