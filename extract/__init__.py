from .utils import jid_to_abbr
from .common import (
    extract_simple_pdf,
    extract_line_numbered_pdf,
    extract_pre_tag_html,
    extract_sometimes_numbered_pdf,
    extract_from_p_tags_html,
    extract_from_code_tags_html,
)
from .az import extract_from_div_html


CONVERSION_FUNCTIONS = {
    "al": extract_line_numbered_pdf,
    "ak": extract_pre_tag_html,
    "az": extract_from_div_html,
    "ar": extract_sometimes_numbered_pdf,
    "co": extract_sometimes_numbered_pdf,
    "ct": extract_from_p_tags_html,
    "id": extract_line_numbered_pdf,
    "il": extract_from_code_tags_html,
    "nc": extract_line_numbered_pdf,
}


def extract_text(data, metadata):
    func = CONVERSION_FUNCTIONS.get(
        jid_to_abbr(metadata["jurisdiction_id"]), lambda data, metadata: ""
    )
    return func(data, metadata)
