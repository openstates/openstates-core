import os
import re
import string
import tempfile
import subprocess


def jid_to_abbr(j):
    return j.split(":")[-1].split("/")[0]


# from pupa.utils.generic import convert_pdf
def convert_pdf(filename, type="xml"):
    commands = {
        "text": ["pdftotext", "-layout", filename, "-"],
        "text-nolayout": ["pdftotext", filename, "-"],
        "xml": ["pdftohtml", "-xml", "-stdout", filename],
        "html": ["pdftohtml", "-stdout", filename],
    }
    try:
        pipe = subprocess.Popen(commands[type], stdout=subprocess.PIPE, close_fds=True).stdout
    except OSError as e:
        raise EnvironmentError(
            "error running %s, missing executable? [%s]" % " ".join(commands[type]), e
        )
    data = pipe.read()
    pipe.close()
    return data


def pdfdata_to_text(data):
    with tempfile.NamedTemporaryFile(delete=True) as tmpf:
        tmpf.write(data)
        tmpf.flush()
        return convert_pdf(tmpf.name, "text").decode("utf8")


def worddata_to_text(data):
    desc, txtfile = tempfile.mkstemp(prefix="tmp-worddata-", suffix=".txt")
    try:
        with tempfile.NamedTemporaryFile(delete=True) as tmpf:
            tmpf.write(data)
            tmpf.flush()
            subprocess.check_call(["timeout", "10", "abiword", "--to=%s" % txtfile, tmpf.name])
            f = open(txtfile)
            text = f.read()
            tmpf.close()
            f.close()
    finally:
        os.remove(txtfile)
        os.close(desc)
    return text.decode("utf8")


PUNCTUATION = re.compile("[%s]" % re.escape(string.punctuation))


def clean(text):
    text = text.replace("\xa0", " ")  # nbsp -> sp
    text = PUNCTUATION.sub(" ", text)  # strip punctuation
    text = re.sub(r"[ \t]", " ", text)  # collapse spaces
    # collapse newlines too?
    return text


def text_after_line_numbers(lines):
    text = []
    for line in lines.splitlines():
        # real bill text starts with an optional space, line number,
        # more spaces, then real text
        match = re.match(r"\s*\d+\s+(.*)", line)
        if match:
            text.append(match.group(1))

    # return all real bill text joined w/ newlines
    return "\n".join(text)
