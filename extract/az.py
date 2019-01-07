from .utils import clean, text_from_element_lxml


def extract_from_div_html(data, metadata):
    """
    AK has the bill text inside <div class="WordSection2">
    """

    text_inside_matching_tag = text_from_element_lxml(data, ".//div[@class='WordSection2']")
    return clean(text_inside_matching_tag)
