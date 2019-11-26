import re
import tempfile
import functools
import subprocess

from lxml import html


def jid_to_abbr(j):
    return j.split(":")[-1].split("/")[0]


def abbr_to_jid(abbr):
    if abbr == "pr":
        return "ocd-jurisdiction/country:us/territory:pr/government"
    elif abbr == "dc":
        return "ocd-jurisdiction/country:us/district:dc/government"
    else:
        return f"ocd-jurisdiction/country:us/state:{abbr}/government"


def pdfdata_to_text(data):
    with tempfile.NamedTemporaryFile(delete=True) as tmpf:
        tmpf.write(data)
        tmpf.flush()
        try:
            pipe = subprocess.Popen(
                ["pdftotext", "-layout", tmpf.name, "-"], stdout=subprocess.PIPE, close_fds=True
            ).stdout
        except OSError as e:
            raise EnvironmentError(f"error running pdftotext, missing executable? [{e}]")
        data = pipe.read()
        pipe.close()
        return data.decode("utf8", "ignore")


def clean(text):
    text = text.replace("\xa0", " ")  # nbsp -> sp
    text = text.replace("\r\n", "\n")  # replace carriage returns
    text = re.sub(r"[ \t]", " ", text)  # collapse spaces
    # collapse newlines too?
    return text


def _text_near_line_numbers(lines, regex):
    """ used for before & after line numbers """
    text = []
    for line in lines.splitlines():
        # real bill text starts with an optional space, line number,
        # more spaces, then real text
        match = re.match(regex, line)
        if match:
            text.append(match.group(1))

    # return all real bill text joined w/ newlines
    return "\n".join(text)


text_after_line_numbers = functools.partial(_text_near_line_numbers, regex=r"\s*\d+\s+(.*)")
text_before_line_numbers = functools.partial(_text_near_line_numbers, regex=r"(.*?)\s+\d+\s*")


def text_from_element_lxml(data, lxml_query):
    html_document = html.fromstring(data)
    matching_elements = html_document.findall(lxml_query)

    # To ensure that we exit non-zero if there are multiple matching elements
    # on the page, raise an exception: this means that the extraction
    # code needs to be updated.
    assert len(matching_elements) == 1, f"{len(matching_elements)} matches for {lxml_query}"

    text_inside_element = matching_elements[0].text_content()
    return text_inside_element


def text_from_element_xpath(data, lxml_xpath_query):
    html_document = html.fromstring(data)
    matching_elements = html_document.xpath(lxml_xpath_query)

    # To ensure that we exit non-zero if there are multiple matching elements
    # on the page, raise an exception: this means that the extraction
    # code needs to be updated.
    assert len(matching_elements) == 1, f"{len(matching_elements)} matches for {lxml_xpath_query}"

    text_inside_element = matching_elements[0].text_content()
    return text_inside_element


def text_from_element_siblings_lxml(data, lxml_query):
    html_document = html.fromstring(data)
    matching_elements = html_document.findall(lxml_query)

    text_inside_elements = ""
    for element in matching_elements:
        text_inside_elements += element.text_content() + "\n"

    return text_inside_elements


def text_from_element_siblings_xpath(data, lxml_query):
    html_document = html.fromstring(data)
    matching_elements = html_document.xpath(lxml_query)

    text_inside_elements = ""
    for element in matching_elements:
        text_inside_elements += element.text_content() + "\n"

    return text_inside_elements
