from lxml import html

from .utils import pdfdata_to_text, text_after_line_numbers


def extract_simple_pdf(data, metadata):
    return pdfdata_to_text(data)


def extract_line_numbered_pdf(data, metadata):
    return text_after_line_numbers(pdfdata_to_text(data))


def extract_pre_tag_html(data, metadata):
    """
    Many states that provide bill text on HTML webpages (e.g. AK, FL)
    have the text inside <pre> tags (for preformatted text).
    """

    html_document = html.fromstring(data)
    pre_tags = html_document.findall(".//pre")

    # To ensure that we exit non-zero if there are multiple <pre> tags
    # on the page, raise an exception: this means that the extraction
    # code needs to be updated.
    assert len(pre_tags) == 1

    text_inside_pre_tag = pre_tags[0].text_content()

    return text_after_line_numbers(text_inside_pre_tag)
