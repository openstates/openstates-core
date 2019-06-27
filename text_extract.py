import os

import csv
import click
import dj_database_url
import django
import scrapelib
from django.conf import settings
from django.db.models import F

from extract.utils import jid_to_abbr
from extract import extract_text

scraper = scrapelib.Scraper()

MIMETYPES = {
    "application/pdf": "pdf",
    "text/html": "html",
    "application/msword": "doc",
    "application/rtf": "rtf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
}


def init_django():
    DATABASE_URL = os.environ.get("DATABASE_URL", "postgis://localhost/cleanos")
    DATABASES = {"default": dj_database_url.parse(DATABASE_URL)}
    settings.configure(
        DATABASES=DATABASES, INSTALLED_APPS=("opencivicdata.core", "opencivicdata.legislative")
    )
    django.setup()


def download(version):
    abbr = jid_to_abbr(version["jurisdiction_id"])
    ext = MIMETYPES[version["media_type"]]
    filename = f'raw/{abbr}/{version["session"]}-{version["identifier"]}-{version["note"]}.{ext}'

    if not os.path.exists(filename):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError:
            pass
        try:
            _, resp = scraper.urlretrieve(version["url"], filename)
        except Exception:
            print("could not fetch", version["id"])
            return None, None

        return filename, resp.content
    else:
        with open(filename, "rb") as f:
            return filename, f.read()


def extract_to_file(filename, data, version):
    text = extract_text(data, version)

    if not text:
        return None, 0

    text_filename = filename.replace("raw/", "text/") + ".txt"
    try:
        os.makedirs(os.path.dirname(text_filename))
    except OSError:
        pass
    with open(text_filename, "w") as f:
        f.write(text)

    return text_filename, len(text)


@click.group()
def cli():
    init_django()


@cli.command()
@click.argument("state")
def stats(state):
    from opencivicdata.legislative.models import BillVersionLink

    all_versions = BillVersionLink.objects.filter(
        version__bill__legislative_session__jurisdiction__name=state
    )
    missing_text_versions = BillVersionLink.objects.filter(
        version__bill__legislative_session__jurisdiction__name=state, text=""
    )

    print(
        f"{state} is missing text for {missing_text_versions.count()} out of {all_versions.count()}"
    )


@cli.command()
@click.argument("state")
def sample(state):
    with open("sample.csv") as f:
        for version in csv.DictReader(f):
            if jid_to_abbr(version["jurisdiction_id"]) == state:
                filename, data = download(version)
                if not filename:
                    continue
                text_filename, bytes = extract_to_file(filename, data, version)
                print(f"{filename} => {text_filename} ({bytes} bytes)")


def extract_metadata(vlink):
    return {
        "url": vlink.url,
        "jurisdiction_id": vlink.version.bill.legislative_session.jurisdiction_id,
    }


@cli.command()
@click.argument("state")
@click.option("-n", default=100)
def update(state, n):
    from opencivicdata.legislative.models import BillVersionLink

    missing_text_versions = BillVersionLink.objects.filter(
        version__bill__legislative_session__jurisdiction__name=state, text=""
    )[:n]

    print(missing_text_versions.count())

    for v in missing_text_versions:
        data = scraper.get(v.url).content
        metadata = extract_metadata(v)
        v.text = extract_text(data, metadata)
        v.save()

if __name__ == "__main__":
    cli()
