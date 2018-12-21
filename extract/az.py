from lxml import html

from .utils import clean


def extract_from_div_html(data, metadata):
    """
    AK has the bill text inside <div class="WordSection2">
    """

    html_document = html.fromstring(data)
    div_tags = html_document.findall(".//div[@class='WordSection2']")

    # To ensure that we exit non-zero if there are multiple matching
    # tags on the page, raise an exception: this means an update is needed.
    assert len(div_tags) == 1

    return clean(div_tags[0].text_content())
