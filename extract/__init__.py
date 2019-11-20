from .utils import jid_to_abbr
from .common import (
    # extract_simple_pdf,
    extract_line_numbered_pdf,
    extract_pre_tag_html,
    extract_sometimes_numbered_pdf,
    extract_from_p_tags_html,
    extractor_for_elements_by_class,
    # extractor_for_element_by_id,
    extractor_for_element_by_xpath,
    extract_from_code_tags_html,
)
from .de import handle_delaware


class DoNotDownload:
    """ Sentinel to indicate that nothing should be downloaded """


CONVERSION_FUNCTIONS = {
    "al": {"application/pdf": extract_line_numbered_pdf},
    # "ak": {"text/html": extract_pre_tag_html},
    "az": {
        "text/html": extractor_for_elements_by_class("WordSection2"),
        "application/pdf": DoNotDownload,
    },
    "ar": {"application/pdf": extract_sometimes_numbered_pdf},
    "ca": {
        "text/html": extractor_for_element_by_xpath(
            './/div[@id="bill"] | .//span[@class="Resolution"]'
        )
    },
    "co": {"application/pdf": extract_sometimes_numbered_pdf},
    "ct": {"text/html": extract_from_p_tags_html, "application/pdf": DoNotDownload},
    "de": {
        "text/html": handle_delaware,
        "application/pdf": handle_delaware,
        "application/msword": DoNotDownload,
    },
    "fl": {"text/html": extract_pre_tag_html, "application/pdf": extract_line_numbered_pdf},
    "ga": {"application/pdf": extract_sometimes_numbered_pdf},
    "hi": {
        "text/html": extractor_for_element_by_xpath(
            './/*[@class="Section2"] | .//*[@class="WordSection2"]'
        ),
        "application/pdf": DoNotDownload,
    },
    "ia": {"application/pdf": extract_line_numbered_pdf, "text/html": DoNotDownload},
    "id": {"application/pdf": extract_line_numbered_pdf},
    "il": {"text/html": extract_from_code_tags_html},
    "ks": {"application/pdf": extract_sometimes_numbered_pdf},
    "la": {"application/pdf": extract_sometimes_numbered_pdf},
    "ma": {"application/pdf": extract_line_numbered_pdf},
    "md": {"application/pdf": extract_line_numbered_pdf},
    "me": {
        "text/html": extractor_for_elements_by_class("billtextbody"),
        "application/rtf": DoNotDownload,
        "application/pdf": DoNotDownload,
    },
    "mi": {"text/html": extractor_for_element_by_xpath('.//*[@class="WordSection1"]')},
    "ms": {
        "text/html": extractor_for_element_by_xpath('.//*[@class="WordSection1"]'),
        "application/pdf": extract_line_numbered_pdf,
    },
    "mt": {"application/pdf": extract_sometimes_numbered_pdf},
    "nc": {"application/pdf": extract_sometimes_numbered_pdf},
    "nd": {"application/pdf": extract_sometimes_numbered_pdf},
    "ne": {"application/pdf": extract_sometimes_numbered_pdf},
    "nv": {"application/pdf": extract_sometimes_numbered_pdf},
    "ok": {"application/pdf": extract_sometimes_numbered_pdf},
    "sc": {"text/html": extract_from_p_tags_html},
    "sd": {"text/html": extractor_for_elements_by_class("fullContent")},
    "ri": {"application/pdf": extract_sometimes_numbered_pdf},
    "wi": {"application/pdf": extract_sometimes_numbered_pdf, "text/html": DoNotDownload},
    "wy": {"application/pdf": extract_sometimes_numbered_pdf},
}


def get_extract_func(metadata):
    try:
        state = jid_to_abbr(metadata["jurisdiction_id"])
        func = CONVERSION_FUNCTIONS[state][metadata["media_type"]]
    except KeyError:
        # TODO: log missing functions once we're further along
        print(f"no function for {state}, {metadata['media_type']}")
        return lambda data, metadata: ""
    return func
