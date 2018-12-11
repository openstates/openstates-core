from .utils import jid_to_abbr
from .common import extract_simple_pdf, extract_line_numbered_pdf


CONVERSION_FUNCTIONS = {
    'nc': extract_line_numbered_pdf,
}


def extract_text(data, version):
    func = CONVERSION_FUNCTIONS[jid_to_abbr(version['jurisdiction_id'])]
    return func(data, version)
