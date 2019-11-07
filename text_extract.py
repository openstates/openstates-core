import os

import csv
import click
import dj_database_url
import django
import scrapelib
from django.conf import settings
from django.db.models import F
from django.contrib.postgres.search import SearchVector

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


def update_bill(bill):
    from opencivicdata.legislative.models import SearchableBill

    try:
        latest_version = bill.versions.order_by("-date", "-note").prefetch_related("links")[0]
    except IndexError:
        return

    # check if there's an old entry and we can use it
    # if bill.searchable:
    #     if bill.searchable.version_id == latest_version.id and not bill.searchable.is_error:
    #         return      # nothing to do
    #     bill.searchable.delete()

    # iterate through versions until we extract some good text
    is_error = True
    raw_text = ""
    for link in latest_version.links.all():
        try:
            data = scraper.get(link.url).content
        except Exception as e:
            continue
        metadata = {
            "url": link.url,
            "media_type": link.media_type,
            "title": bill.title,
            "jurisdiction_id": bill.legislative_session.jurisdiction_id,
        }
        # TODO: clean up whitespace
        try:
            raw_text = extract_text(data, metadata)
        except Exception as e:
            print(e)
            continue

        if raw_text:
            is_error = False
            break

    sb = SearchableBill.objects.create(
        bill=bill,
        version_link=link,
        all_titles=bill.title,  # TODO: add other titles
        raw_text=raw_text,
        is_error=is_error,
        search_vector="",
    )
    return sb.id


@click.group()
def cli():
    init_django()


@cli.command()
@click.argument("state")
def stats(state):
    from opencivicdata.legislative.models import Bill

    all_bills = Bill.objects.filter(legislative_session__jurisdiction__name=state)
    missing_search = Bill.objects.filter(
        legislative_session__jurisdiction__name=state, searchable__isnull=True
    )

    print(f"{state} is missing text for {missing_search.count()} out of {all_bills.count()}")


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


@cli.command()
@click.argument("state")
@click.option("-n", default=100)
def update(state, n):
    from opencivicdata.legislative.models import Bill, SearchableBill

    missing_search = Bill.objects.filter(
        legislative_session__jurisdiction__name=state, searchable__isnull=True
    )[:n]

    ids_to_update = []
    for b in missing_search:
        ids_to_update.append(update_bill(b))

    print(f"updating {len(ids_to_update)} search vectors")
    SearchableBill.objects.filter(id__in=ids_to_update).update(
        search_vector=(
            SearchVector("all_titles", weight="A", config="english")
            + SearchVector("raw_text", weight="B", config="english")
        )
    )


if __name__ == "__main__":
    cli()
