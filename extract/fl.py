from .common import (
    extractor_for_element_by_xpath,
    extract_line_numbered_pdf,
    extract_pre_tag_html
)

from .utils import (
    text_after_line_numbers
)

def handle_florida(data, metadata):
    if metadata["media_type"] == "text/html":
        # lines = extract_pre_tag_html(data, metadata)
        # return text_after_line_numbers(lines)
        return extract_pre_tag_html(data,metadata)
    elif metadata["media_type"] == "application/pdf":
        return extract_line_numbered_pdf(data, metadata)
    else:
        print("unexpected media type in florida", metadata["media_type"])
        assert False