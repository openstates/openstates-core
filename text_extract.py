#!/usr/bin/env python
import os
import sys
import csv
import math
import warnings
import click
import dj_database_url
import django
import scrapelib
from django.contrib.postgres.search import SearchVector
from django.db import transaction

from extract.utils import jid_to_abbr, abbr_to_jid
from extract import get_extract_func, DoNotDownload, CONVERSION_FUNCTIONS

# disable SSL validation and ignore warnings
scraper = scrapelib.Scraper(verify=False)
scraper.user_agent = "Mozilla"
warnings.filterwarnings("ignore", module="urllib3")


MIMETYPES = {
    "application/pdf": "pdf",
    "text/html": "html",
    "application/msword": "doc",
    "application/rtf": "rtf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
}


def init_django():
    from django.conf import settings

    DATABASE_URL = os.environ.get("DATABASE_URL", "postgis://localhost/openstatesorg")
    DATABASES = {"default": dj_database_url.parse(DATABASE_URL)}
    settings.configure(
        DATABASES=DATABASES, INSTALLED_APPS=("opencivicdata.core", "opencivicdata.legislative")
    )
    django.setup()


def download(version):
    abbr = jid_to_abbr(version["jurisdiction_id"])
    ext = MIMETYPES[version["media_type"]]
    filename = f'raw/{abbr}/{version["session"]}-{version["identifier"]}-{version["note"]}.{ext}'
    filename.replace("#", "__")

    if not os.path.exists(filename):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError:
            pass
        try:
            _, resp = scraper.urlretrieve(version["url"], filename)
        except Exception:
            click.secho("could not fetch " + version["url"], fg="yellow")
            return None, None

        return filename, resp.content
    else:
        with open(filename, "rb") as f:
            return filename, f.read()


def extract_to_file(filename, data, version):
    try:
        func = get_extract_func(version)
        if func == DoNotDownload:
            return DoNotDownload, 0
        else:
            text = func(data, version)
    except Exception as e:
        click.secho(f"exception processing {version['url']}: {e}", fg="red")
        text = None

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
        links = latest_version.links.all()
    except IndexError:
        links = []

    # check if there's an old entry and we can use it
    # if bill.searchable:
    #     if bill.searchable.version_id == latest_version.id and not bill.searchable.is_error:
    #         return      # nothing to do
    #     bill.searchable.delete()

    # iterate through versions until we extract some good text
    is_error = True
    raw_text = ""
    link = None
    for link in links:
        metadata = {
            "url": link.url,
            "media_type": link.media_type,
            "title": bill.title,
            "jurisdiction_id": bill.legislative_session.jurisdiction_id,
        }
        func = get_extract_func(metadata)
        if func == DoNotDownload:
            continue
        try:
            data = scraper.get(link.url).content
        except Exception:
            continue
        # TODO: clean up whitespace
        try:
            raw_text = func(data, metadata)
        except Exception as e:
            click.secho(f"exception processing {metadata['url']}: {e}", fg="red")

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
    pass


def _resample(state, n=50):
    """
    Grab new versions for a state from the database.
    """
    init_django()
    from opencivicdata.legislative.models import BillVersion

    versions = BillVersion.objects.filter(
        bill__legislative_session__jurisdiction_id=abbr_to_jid(state)
    ).order_by("?")[:n]

    count = 0
    fieldnames = [
        "id",
        "session",
        "identifier",
        "title",
        "jurisdiction_id",
        "media_type",
        "url",
        "note",
    ]

    with open(f"raw/{state}.csv", "w") as outf:
        out = csv.DictWriter(outf, fieldnames=fieldnames)
        out.writeheader()
        for v in versions:
            for link in v.links.all():
                out.writerow(
                    {
                        "id": v.id,
                        "session": v.bill.legislative_session.identifier,
                        "jurisdiction_id": v.bill.legislative_session.jurisdiction_id,
                        "identifier": v.bill.identifier,
                        "title": v.bill.title,
                        "url": link.url,
                        "media_type": link.media_type,
                        "note": v.note,
                    }
                )
                count += 1
    click.secho(f"wrote new sample csv with {count} records")


@cli.command()
@click.argument("state")
@click.option("--resample/--no-resample", default=False)
@click.option("--quiet/--no-quiet", default=False)
def sample(state, resample, quiet):
    if resample:
        _resample(state)
    count = missing = empty = skipped = 0
    with open(f"raw/{state}.csv") as f:
        for version in csv.DictReader(f):
            count += 1
            filename, data = download(version)
            if not filename:
                missing += 1
                continue
            text_filename, n_bytes = extract_to_file(filename, data, version)
            if text_filename == DoNotDownload:
                skipped += 1
            elif not n_bytes:
                empty += 1
            if not quiet:
                click.secho(f"{filename} => {text_filename} ({n_bytes} bytes)")
    # decide and print result
    status = "green"
    if empty or missing:  # arbitrary threshold for now
        status = "red"
    click.secho(
        f"{state}: processed {count}, {skipped} skipped, {missing} missing, {empty} empty",
        fg=status,
    )
    if status == "red":
        return 1
    return 0


@cli.command()
@click.pass_context
def test(ctx):
    failures = 0
    states = sorted(CONVERSION_FUNCTIONS.keys())
    click.secho(f"testing {len(states)} states...", fg="white")
    for state in states:
        failures += ctx.invoke(sample, state=state, quiet=True)
    sys.exit(failures)


@cli.command()
def status():
    init_django()
    from opencivicdata.legislative.models import Bill

    states = sorted(CONVERSION_FUNCTIONS.keys())
    click.secho("state |  bills  | missing | errors ", fg="white")
    click.secho("===================================", fg="white")
    for state in states:
        all_bills = Bill.objects.filter(legislative_session__jurisdiction_id=abbr_to_jid(state))
        missing_search = all_bills.filter(searchable__isnull=True).count()
        errors = all_bills.filter(searchable__is_error=True).count()
        all_bills = all_bills.count()

        errcolor = mscolor = "green"
        if missing_search > 0:
            missing_search = math.ceil(missing_search / all_bills * 100)
            mscolor = "yellow"
        if missing_search > 1:
            mscolor = "red"
        if errors > 0:
            errcolor = "yellow"
            errors = math.ceil(errors / all_bills * 100)
        if errors > 5:
            errcolor = "red"

        click.echo(
            f"{state:5} | {all_bills:7} | "
            + click.style(f"{missing_search:6}%", fg=mscolor)
            + " | "
            + click.style(f"{errors:6}%", fg=errcolor)
        )


@cli.command()
@click.argument("state")
@click.option("-n", default=None)
def update(state, n):
    init_django()
    from opencivicdata.legislative.models import Bill

    # configure how often to print and checkpoint
    STATUS_NUM = 100
    CHECKPOINT_NUM = 500

    all_bills = Bill.objects.filter(legislative_session__jurisdiction_id=abbr_to_jid(state))
    missing_search = all_bills.filter(searchable__isnull=True)
    print(f"{state}: {len(all_bills)} bills, {len(missing_search)} without search results")
    if n:
        missing_search = missing_search[:n]
    else:
        n = len(missing_search)

    ids_to_update = []
    updated_count = 0

    # going to manage our own transactions here so we can save in chunks
    transaction.set_autocommit(False)

    for b in missing_search:
        ids_to_update.append(update_bill(b))
        updated_count += 1
        if updated_count % STATUS_NUM == 0:
            print(f"{state}: updated {updated_count} out of {n}")
        if updated_count % CHECKPOINT_NUM == 0:
            reindex(ids_to_update)
            transaction.commit()
            ids_to_update = []

    # be sure to reindex final set
    reindex(ids_to_update)
    transaction.commit()
    transaction.set_autocommit(True)


def reindex(ids_to_update):
    from opencivicdata.legislative.models import SearchableBill

    print(f"updating {len(ids_to_update)} search vectors")
    SearchableBill.objects.filter(id__in=ids_to_update).update(
        search_vector=(
            SearchVector("all_titles", weight="A", config="english")
            + SearchVector("raw_text", weight="B", config="english")
        )
    )


if __name__ == "__main__":
    cli()
