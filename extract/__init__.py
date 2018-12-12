from .utils import jid_to_abbr
from .common import extract_simple_pdf, extract_line_numbered_pdf


CONVERSION_FUNCTIONS = {"al": extract_line_numbered_pdf, "nc": extract_line_numbered_pdf}


def extract_text(data, metadata):
    func = CONVERSION_FUNCTIONS.get(
        jid_to_abbr(metadata["jurisdiction_id"]), lambda data, metadata: ""
    )
    return func(data, metadata)
