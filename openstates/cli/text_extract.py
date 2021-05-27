#!/usr/bin/env python
import os
import typing
import sys
import csv
import math
import warnings
import click
import scrapelib
from pathlib import Path
from django.contrib.postgres.search import SearchVector  # type: ignore
from django.db import transaction  # type: ignore
from django.db.models import Count  # type: ignore
from openstates.utils.django import init_django
from openstates.utils import jid_to_abbr, abbr_to_jid
from openstates.fulltext import (
    get_extract_func,
    DoNotDownload,
    CONVERSION_FUNCTIONS,
    Metadata,
)

# disable SSL validation and ignore warnings
scraper = scrapelib.Scraper(verify=False)
scraper.user_agent = "Mozilla"
warnings.filterwarnings("ignore", module="urllib3")


def get_raw_dir() -> Path:
    return Path(__file__).parent / ".." / "fulltext" / "raw"


MIMETYPES = {
    "application/pdf": "pdf",
    "text/html": "html",
    "application/msword": "doc",
    "application/rtf": "rtf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
}


def _cleanup(text: str) -> str:
    # strip nulls
    return text.replace("\0", "")


def download(
    version: dict[str, str]
) -> tuple[typing.Optional[str], typing.Optional[bytes]]:
    abbr = jid_to_abbr(version["jurisdiction_id"])
    ext = MIMETYPES[version["media_type"]]
    filename = str(
        get_raw_dir()
        / f'{abbr}/{version["session"]}-{version["identifier"]}-{version["note"]}.{ext}'
    )
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


def extract_to_file(
    filename: str, data: bytes, version: Metadata
) -> tuple[typing.Union[None, str, typing.Type[DoNotDownload]], int]:
    text: typing.Optional[str]
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


def update_bill(bill: typing.Any) -> int:
    from openstates.data.models import SearchableBill

    try:
        latest_version = bill.versions.order_by("-date", "-note").prefetch_related(
            "links"
        )[0]
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
        metadata: Metadata = {
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
        try:
            raw_text = func(data, metadata)
        except Exception as e:
            click.secho(f"exception processing {metadata['url']}: {e}", fg="red")

        # TODO: clean up whitespace
        raw_text = _cleanup(raw_text)

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
def main() -> None:
    pass


def _resample(state: str, n: int = 50) -> None:
    """
    Grab new versions for a state from the database.
    """
    init_django()
    from openstates.data.models import BillVersion

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

    with open(get_raw_dir() / f"{state}.csv", "w") as outf:
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


@main.command(help="obtain a sample of bills to extract text from")
@click.argument("state")
@click.option("--resample/--no-resample", default=False)
@click.option("--quiet/--no-quiet", default=False)
def sample(state: str, resample: bool, quiet: bool) -> int:
    if resample:
        _resample(state)
    count = missing = empty = skipped = 0
    with open(get_raw_dir() / f"{state}.csv") as f:
        for version in csv.DictReader(f):
            count += 1
            filename, data = download(version)
            if not filename or not data:
                missing += 1
                continue
            text_filename, n_bytes = extract_to_file(
                filename, data, typing.cast(Metadata, version)
            )
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


@main.command(help="run sample on all states, used for CI")
@click.pass_context
def test(ctx: typing.Any) -> None:
    failures = 0
    states = sorted(CONVERSION_FUNCTIONS.keys())
    click.secho(f"testing {len(states)} states...", fg="white")
    for state in states:
        failures += ctx.invoke(sample, state=state, quiet=True)
    sys.exit(failures)


@main.command(help="print a status table showing the current condition of states")
def status() -> None:
    init_django()
    from openstates.data.models import Bill

    states = sorted(CONVERSION_FUNCTIONS.keys())
    click.secho("state |  bills  | missing | errors ", fg="white")
    click.secho("===================================", fg="white")
    for state in states:
        all_bills = Bill.objects.filter(
            legislative_session__jurisdiction_id=abbr_to_jid(state)
        )
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


@main.command(help="rebuild the search index objects for a given state")
@click.argument("state")
def reindex_state(state: str) -> None:
    init_django()
    from openstates.data.models import SearchableBill

    ids = list(
        SearchableBill.objects.filter(
            bill__legislative_session__jurisdiction_id=abbr_to_jid(state)
        ).values_list("id", flat=True)
    )
    print(f"reindexing {len(ids)} bills for state")
    reindex(ids)


@main.command(help="update the saved bill text in the database")
@click.argument("state")
@click.option("-n", default=None)
@click.option("--clear-errors/--no-clear-errors", default=False)
@click.option("--checkpoint", default=500)
def update(state: str, n: int, clear_errors: bool, checkpoint: int) -> None:
    init_django()
    from openstates.data.models import Bill, SearchableBill

    # print status within checkpoints
    status_num = checkpoint / 5

    if state == "all":
        all_bills = Bill.objects.all()
    else:
        all_bills = Bill.objects.filter(
            legislative_session__jurisdiction_id=abbr_to_jid(state)
        )

    if clear_errors:
        if state == "all":
            print("--clear-errors only works with specific states, not all")
            return
        errs = SearchableBill.objects.filter(bill__in=all_bills, is_error=True)
        print(f"clearing {len(errs)} errors")
        errs.delete()

    missing_search = all_bills.filter(searchable__isnull=True)
    if state == "all":
        MAX_UPDATE = 1000
        aggregates = missing_search.values(
            "legislative_session__jurisdiction__name"
        ).annotate(count=Count("id"))
        for agg in aggregates:
            state_name = agg["legislative_session__jurisdiction__name"]
            if agg["count"] > MAX_UPDATE:
                click.secho(
                    f"Too many bills to update for {state_name}: {agg['count']}, skipping",
                    fg="red",
                )
                missing_search = missing_search.exclude(
                    legislative_session__jurisdiction__name=state_name
                )
        print(f"{len(missing_search)} missing, updating")
    else:
        print(
            f"{state}: {len(all_bills)} bills, {len(missing_search)} without search results"
        )

    if n:
        missing_search = missing_search[: int(n)]
    else:
        n = len(missing_search)

    ids_to_update = []
    updated_count = 0

    # going to manage our own transactions here so we can save in chunks
    transaction.set_autocommit(False)

    for b in missing_search:
        ids_to_update.append(update_bill(b))
        updated_count += 1
        if updated_count % status_num == 0:
            print(f"{state}: updated {updated_count} out of {n}")
        if updated_count % checkpoint == 0:
            reindex(ids_to_update)
            transaction.commit()
            ids_to_update = []

    # be sure to reindex final set
    reindex(ids_to_update)
    transaction.commit()
    transaction.set_autocommit(True)


def reindex(ids_to_update: list[int]) -> None:
    from openstates.data.models import SearchableBill

    print(f"updating {len(ids_to_update)} search vectors")
    res = SearchableBill.objects.filter(id__in=ids_to_update).update(
        search_vector=(
            SearchVector("all_titles", weight="A", config="english")
            + SearchVector("raw_text", weight="B", config="english")
        )
    )
    print(f"updated {res}")


if __name__ == "__main__":
    main()
