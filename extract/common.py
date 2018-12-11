from .utils import pdfdata_to_text, text_after_line_numbers


def extract_simple_pdf(data, metadata):
    return pdfdata_to_text(data)


def extract_line_numbered_pdf(data, metadata):
    return text_after_line_numbers(pdfdata_to_text(data))
