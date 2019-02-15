from .utils import jid_to_abbr
from .common import (
    extract_simple_pdf,
    extract_line_numbered_pdf,
    extract_pre_tag_html,
    extract_sometimes_numbered_pdf,
    extract_from_p_tags_html,
    extractor_for_elements_by_class,
    extractor_for_element_by_id,
    extractor_for_element_by_xpath
)
from .de import handle_delaware

CONVERSION_FUNCTIONS = {
    "al": extract_line_numbered_pdf,
    "ak": extract_pre_tag_html,
    "az": extractor_for_elements_by_class('WordSection2'),
    "ar": extract_sometimes_numbered_pdf,
    "co": extract_sometimes_numbered_pdf,
    "ct": extract_from_p_tags_html,
    "nc": extract_line_numbered_pdf,
    # il done in PR from redshiftzero
    # id done in PR from redshiftzero
    "ca": {
        "text/html": extractor_for_element_by_xpath('.//div[@id="bill"] | .//span[@class="Resolution"]'),    
    },
    "de": handle_delaware,
    "fl": {
        "text/html": extract_pre_tag_html,
        "application/pdf":  extract_line_numbered_pdf,
    },
    "hi": {
        "text/html": extractor_for_element_by_xpath('.//*[@class="Section2"] | .//*[@class="WordSection2"]')
    }
}


def extract_text(data, metadata):
    func_or_dict = CONVERSION_FUNCTIONS.get(
        jid_to_abbr(metadata["jurisdiction_id"]), lambda data, metadata: ""
    )
    if isinstance(func_or_dict, dict):
        func = func_or_dict.get(metadata["media_type"], lambda data, metadata: "")
    else:
        func = func_or_dict
    return func(data, metadata)
