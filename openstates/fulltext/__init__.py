from openstates.utils import jid_to_abbr
from .common import (
    extract_simple_pdf,
    extract_line_numbered_pdf,
    extract_line_post_numbered_pdf,
    extract_pre_tag_html,
    extract_sometimes_numbered_pdf,
    extract_from_p_tags_html,
    extractor_for_elements_by_class,
    extractor_for_element_by_id,
    extractor_for_element_by_xpath,
    extract_from_code_tags_html,
    textract_extractor,
    Metadata,
    ExtractorFunc,
)
from .de import handle_delaware


class DoNotDownload:
    """ Sentinel to indicate that nothing should be downloaded """


DOCX_MIMETYPE = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)

CONVERSION_FUNCTIONS = {
    "al": {"application/pdf": extract_line_numbered_pdf},
    "ak": {"text/html": extractor_for_element_by_id("draftOverlay")},
    "az": {
        "text/html": extractor_for_elements_by_class("WordSection2"),
        "application/pdf": DoNotDownload,
    },
    "ar": {"application/pdf": extract_sometimes_numbered_pdf},
    "ca": {
        "text/html": extractor_for_element_by_xpath(
            './/div[@id="bill"] | .//span[@class="Resolution"]'
        ),
        "application/pdf": extract_sometimes_numbered_pdf,
    },
    "co": {"application/pdf": extract_sometimes_numbered_pdf},
    "ct": {"text/html": extract_from_p_tags_html, "application/pdf": DoNotDownload},
    "dc": {"application/pdf": textract_extractor(extension="pdf", method="tesseract")},
    "de": {
        "text/html": handle_delaware,
        "application/pdf": handle_delaware,
        "application/msword": DoNotDownload,
    },
    "fl": {
        "text/html": extract_pre_tag_html,
        "application/pdf": extract_line_numbered_pdf,
    },
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
    "in": {"application/pdf": extract_sometimes_numbered_pdf},
    "ks": {"application/pdf": extract_sometimes_numbered_pdf},
    "ky": {"application/pdf": extract_line_numbered_pdf},
    "la": {"application/pdf": extract_sometimes_numbered_pdf},
    "ma": {"application/pdf": extract_line_numbered_pdf},
    "md": {"application/pdf": extract_line_numbered_pdf},
    "me": {
        "text/html": extractor_for_elements_by_class("billtextbody"),
        "application/rtf": DoNotDownload,
        "application/pdf": DoNotDownload,
    },
    "mi": {"text/html": extractor_for_element_by_xpath('.//*[@class="WordSection1"]')},
    "mo": {"application/pdf": extract_line_numbered_pdf},
    "mn": {"text/html": extractor_for_element_by_id("document")},
    "ms": {
        "text/html": extractor_for_element_by_xpath('.//*[@class="WordSection1"]'),
        "application/pdf": extract_line_numbered_pdf,
    },
    "mt": {"application/pdf": extract_sometimes_numbered_pdf},
    "nc": {"application/pdf": extract_sometimes_numbered_pdf},
    "nd": {"application/pdf": extract_sometimes_numbered_pdf},
    "ne": {"application/pdf": extract_sometimes_numbered_pdf},
    "nh": {
        "application/pdf": extract_sometimes_numbered_pdf,
        "text/html": extract_from_p_tags_html,
    },
    "nj": {"text/html": extractor_for_element_by_xpath('.//*[@class="WordSection3"]')},
    # NY HTML is just summaries
    "ny": {
        "text/html": DoNotDownload,
        "application/pdf": extract_sometimes_numbered_pdf,
    },
    "nm": {
        "application/pdf": extract_sometimes_numbered_pdf,
        "text/html": DoNotDownload,
    },
    "nv": {"application/pdf": extract_sometimes_numbered_pdf},
    "oh": {"application/pdf": extract_line_post_numbered_pdf},
    "or": {"application/pdf": extract_sometimes_numbered_pdf},
    "ok": {"application/pdf": extract_sometimes_numbered_pdf},
    "sc": {"text/html": extract_from_p_tags_html},
    "sd": {"text/html": extractor_for_elements_by_class("fullContent")},
    "tn": {"application/pdf": extract_simple_pdf},
    "ut": {"application/pdf": extract_line_numbered_pdf},
    "pr": {
        "application/msword": textract_extractor(extension="doc"),
        DOCX_MIMETYPE: textract_extractor(extension="docx"),
    },
    "pa": {
        "application/msword": DoNotDownload,
        "text/html": DoNotDownload,
        "application/pdf": extract_line_numbered_pdf,
    },
    "ri": {"application/pdf": extract_sometimes_numbered_pdf},
    # aggressive, but the Washington & Texas HTML are both basically bare
    "tx": {"text/html": extractor_for_element_by_xpath("//html")},
    "va": {"text/html": extractor_for_element_by_id("mainC")},
    "vt": {"application/pdf": extract_sometimes_numbered_pdf},
    "wa": {"text/html": extractor_for_element_by_xpath("//html")},
    "wi": {
        "application/pdf": extract_sometimes_numbered_pdf,
        "text/html": DoNotDownload,
    },
    "wv": {"text/html": extractor_for_element_by_xpath('.//*[@class="textcontainer"]')},
    "wy": {"application/pdf": extract_sometimes_numbered_pdf},
    "us": {
        "text/xml": DoNotDownload,
        "application/pdf": extract_sometimes_numbered_pdf,
    },
}


def get_extract_func(metadata: Metadata) -> ExtractorFunc:
    try:
        state = jid_to_abbr(metadata["jurisdiction_id"])
        # ignore type here because DoNotDownload sentinels were in the way
        func = CONVERSION_FUNCTIONS[state][metadata["media_type"]]  # type: ignore
    except KeyError:
        print(f"no function for {state}, {metadata['media_type']}")
        return lambda data, metadata: ""
    return func
