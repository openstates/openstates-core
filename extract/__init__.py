from .utils import jid_to_abbr
from .common import (
    extract_simple_pdf,
    extract_line_numbered_pdf,
    extract_pre_tag_html,
    extract_sometimes_numbered_pdf,
    extract_from_p_tags_html,
    extractor_for_elements_by_class,
    extractor_for_element_by_id
    extract_from_code_tags_html,
)
from .ca import handle_california
from .de import handle_delaware
from .fl import handle_florida
from .hi import handle_hawaii

CONVERSION_FUNCTIONS = {
    "al": extract_line_numbered_pdf,
    "ak": extract_pre_tag_html,
    "az": extractor_for_elements_by_class('WordSection2'),
    "ar": extract_sometimes_numbered_pdf,
    "co": extract_sometimes_numbered_pdf,
    "ct": extract_from_p_tags_html,
    "id": extract_line_numbered_pdf,
    "il": extract_from_code_tags_html,
    "nc": extract_line_numbered_pdf,
    "ca": handle_california,
    "de": handle_delaware,
    "fl": handle_florida,
    "hi": handle_hawaii
}


def extract_text(data, metadata):
    func = CONVERSION_FUNCTIONS.get(
        jid_to_abbr(metadata["jurisdiction_id"]), lambda data, metadata: ""
    )
    return func(data, metadata)
