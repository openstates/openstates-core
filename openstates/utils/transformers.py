"""
    Transformers for IMPORT_TRANSFORMERS
"""
import re


_bill_id_re = re.compile(r"([A-Z]*)\s*0*([-\d]+)")
_mi_bill_id_re = re.compile(r"(SJR|HJR)\s*([A-Z]+)\s*$")
_whitespace_re = re.compile(r"\s+")


def fix_bill_id(bill_id: str) -> str:
    bill_id = bill_id.upper()
    # special case for MI Joint Resolutions in format "(H|S)JR {letters}"
    if _mi_bill_id_re.match(bill_id):
        return _mi_bill_id_re.sub(r"\1 \2", bill_id, 1).strip()
    return _bill_id_re.sub(r"\1 \2", bill_id, 1).strip()


def collapse_whitespace(value: str) -> str:
    return _whitespace_re.sub(" ", value)
