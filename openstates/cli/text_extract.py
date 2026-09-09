#!/usr/bin/env python
import os
import re
import hashlib
import difflib
import typing
import sys
import csv
import json
import math
import subprocess
import textwrap
import warnings
import click
import requests
import scrapelib
import time
from pathlib import Path
from urllib.parse import urlparse
from django.contrib.postgres.search import SearchVector  # type: ignore
from django.db import transaction, IntegrityError  # type: ignore
from django.db.models import Count  # type: ignore
from django.utils import timezone  # type: ignore
from openstates.utils.django import init_django
from openstates.utils import jid_to_abbr, abbr_to_jid
from openstates.fulltext import (
    get_extract_func,
    DoNotDownload,
    CONVERSION_FUNCTIONS,
    Metadata,
)
from ..utils.instrument import Instrumentation
from ..utils.cookie_provider import (
    BLOCK_PAGE_MARKERS as _BLOCK_PAGE_MARKERS,
    WafBlockDetected,
    content_matches_block_markers,
    content_matches_fake_404_block,
)
from ..utils.resilience_profiles import profile_for_netloc
from ..utils.waf_circuit_breaker import raise_if_waf_block_threshold_reached
from ..utils.version_ordering import (
    STAGE_UNKNOWN as _STAGE_UNKNOWN,
    is_procedural_document as _is_procedural_document,
    note_stage as _note_stage,
    version_sort_key as _version_sort_key,
)
from openstates.exceptions import ScrapeError

stats = Instrumentation()
# disable SSL validation and ignore warnings
scraper = scrapelib.Scraper(verify=False)
scraper.user_agent = "Mozilla"
# Match FL's own scraper's resilience settings (scrapers/fl/bills.py) instead of scrapelib's
# bare defaults (0 retries) -- this scraper hits the same flaky state legislature sites FL's
# scraper does, so it should retry the same way rather than giving up on the first failure.
scraper.retry_attempts = 5
scraper.retry_wait_seconds = 5
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

# Phase 2 (PLAN-bill-document-provenance.md): S3 Glacier Deep Archive upload + verify.
# Always go through the sudo-gated proxy wrapper -- no raw AWS credentials or CLI exist on
# this box by design (see ddp-infra/Production_S3_Wrappers.md).
S3_BILL_ARCHIVE_WRAPPER = "/Users/agentsmith/bin/ddp-prod-s3-bill-archive"
S3_BILL_ARCHIVE_BUCKET = "ddp-bill-archive"

# OPEN-237: how often archive()'s progress heartbeat fires (see its own comment at the call
# site) -- frequent enough that a stalled-run detector polling every few minutes sees it,
# infrequent enough not to flood the log on a large jurisdiction's run.
#
# Deploy ordering: this must ship before ddp-open-states's os-status starts reading the
# heartbeat line it produces -- deployed the other way round, os-status finds no heartbeat
# for any in-flight run and reports every archiver as stalled, even though nothing is
# actually wrong. Same pairing requirement as cloud_archiver.py's OPEN-238 note. Rolling
# back reverses the order: os-status's consumer change goes first, this producer change
# second (or os-status simply tolerates a run of stale results in between).
_ARCHIVE_HEARTBEAT_INTERVAL_S = 60

# Found 2026-07-28: legislature.mi.gov started serving a CAPTCHA/rate-limit challenge page
# (HTTP 200, "Validation request" title) in place of every requested document mid-run. Nothing
# about that response looks wrong at the transport layer, so it was archived and S3-uploaded as
# if it were the real bill text -- 236 documents, silently. These two checks catch that class of
# bug: a binary media_type whose actual bytes don't match that format's own magic number at all,
# or any response containing a known vendor challenge-page fingerprint. Not exhaustive by
# design -- this catches "the site is lying about what it sent us", not every possible malformed
# document.
_BINARY_MAGIC_BYTES = {
    "application/pdf": (b"%PDF-",),
    "application/msword": (b"\xd0\xcf\x11\xe0",),
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": (
        b"PK\x03\x04",
    ),
}
# _BLOCK_PAGE_MARKERS itself now lives in openstates.utils.cookie_provider (OPEN-19) so
# scrapers and this archiver share one block-detection heuristic instead of each keeping
# its own copy that can drift out of sync.


def _block_page_reason(data: bytes, media_type: str) -> typing.Optional[str]:
    magics = _BINARY_MAGIC_BYTES.get(media_type)
    if magics and not any(data.startswith(m) for m in magics):
        return f"expected {media_type} magic bytes, got {data[:16]!r} instead"
    sniff = data[:2048].lower()
    for marker in _BLOCK_PAGE_MARKERS:
        if marker in sniff:
            return f"content matches known block-page marker {marker!r}"
    return None


# Per-profile scrapelib.Scraper instances (OPEN-53) -- lazily created so a WAF-profiled
# jurisdiction's own rate limit doesn't affect (or get affected by) every other jurisdiction
# sharing the plain module-level `scraper` above. Module-level state is fine: each
# `os-text-extract archive` invocation is its own fresh process.
_profile_scrapers: typing.Dict[str, scrapelib.Scraper] = {}

# Per-profile consecutive-WAF-block counters (OPEN-52), same reasoning.
_profile_consecutive_blocks: typing.Dict[str, int] = {}


def _scraper_for_profile(profile) -> scrapelib.Scraper:
    if profile.name not in _profile_scrapers:
        s = scrapelib.Scraper(verify=False)
        s.user_agent = "Mozilla"
        # OPEN-53 (reopened 2026-08-15): retry_attempts=0 here, deliberately unlike the plain
        # module-level `scraper` above -- scrapelib.RetrySession's own retry loop has no
        # per-exception-type exclusion, so a nonzero value here would blindly retry a WAF
        # block (a rejected status, or any exception from the request itself) several times
        # with the same stale cookies before do_request()'s WafBlockDetected handling below
        # ever runs, exactly the "generic retry fires before the cookie-rewarm path engages"
        # failure mode this ticket was filed to describe. CookieProvider.fetch_with_retry's
        # own single invalidate-and-rewarm-once retry is the only retry layer for these
        # profiled fetches now, matching MI's scraper-side mi_waf_get()'s same rationale.
        s.retry_attempts = 0
        s.requests_per_minute = profile.requests_per_minute
        _profile_scrapers[profile.name] = s
    return _profile_scrapers[profile.name]


def _fetch_bytes(url: str) -> bytes:
    """
    GET url via the module-level `scraper` and return its content.

    Jurisdictions with a WAF resilience profile (OPEN-54's `resilience_profiles.py` -- MI and FL
    as of this writing) are wired to that profile's cached WAF cookies, own rate limit (OPEN-53),
    and a consecutive-block circuit breaker (OPEN-52) that aborts the whole archive run (raising
    ScrapeError, letting `archive()` exit non-zero) rather than silently absorbing every fetch as
    one more per-document `fetch_errors` count. Every other jurisdiction's fetch is unchanged.
    Deliberately scoped to this function (used by archive_bill_versions(), the path
    run-archive.sh actually calls) and not the older download()/update_bill() paths used by the
    separate `sample`/`update` commands -- out of scope for this ticket, not an oversight.
    """
    profile = profile_for_netloc(urlparse(url).netloc)
    if profile is not None:
        profile_scraper = _scraper_for_profile(profile)

        def do_request(cookies: dict, user_agent: str) -> requests.Response:
            try:
                # OPEN-23: attach the real User-Agent the cookie provider captured alongside
                # these same cookies -- sending no jurisdiction-specific User-Agent at all was
                # the original cookie/identity mismatch bug this fixed for MI.
                resp = profile_scraper.request(
                    "GET",
                    url,
                    allow_redirects=True,
                    cookies=cookies,
                    headers={"User-Agent": user_agent},
                )
            except requests.exceptions.ConnectionError as e:
                raise WafBlockDetected(str(e)) from e
            except scrapelib.HTTPError as e:
                # OPEN-53 (reopened 2026-08-15): with retry_attempts=0 above, a rejected
                # status now reaches here on the very first attempt instead of being blindly
                # retried by scrapelib itself -- a WAF can serve its block behind a genuine
                # error status (MI's fake-404, see content_matches_fake_404_block's own
                # docstring), not just a 200-status challenge page. Any other real HTTPError
                # (a genuinely dead link, a real server error) is not a WAF signature and
                # must keep propagating unchanged, same as MI's original archiver do_request.
                body = getattr(e.response, "content", None)
                if body is None:
                    body = (e.body or "").encode()
                if content_matches_fake_404_block(body) or content_matches_block_markers(
                    body
                ):
                    raise WafBlockDetected(
                        f"{e.response.status_code if e.response else '?'} response matched "
                        "known WAF block-page heuristic"
                    ) from e
                raise
            if content_matches_block_markers(resp.content):
                raise WafBlockDetected(
                    "response matched known WAF block-page heuristic"
                )
            return resp

        try:
            content = profile.cookie_provider.fetch_with_retry(do_request).content
        except WafBlockDetected as e:
            _profile_consecutive_blocks[profile.name] = (
                _profile_consecutive_blocks.get(profile.name, 0) + 1
            )
            raise_if_waf_block_threshold_reached(
                _profile_consecutive_blocks[profile.name],
                profile.circuit_breaker_max_consecutive_blocks,
                e,
                scrape_label=f"{profile.name} archive fetch",
                fetch_description=f"fetching {url}",
            )
            raise
        else:
            _profile_consecutive_blocks[profile.name] = 0
            return content

    return scraper.request("GET", url, allow_redirects=True).content


def _cleanup(text: str) -> str:
    # strip nulls
    return text.replace("\0", "")


# Arizona's drafting software's own literal section-delimiter tokens (see _reflow_paragraphs()'s
# own docstring, point 1) -- END_STATUTE is always glued to the tail of the preceding sentence
# with no reliable punctuation of its own, so it's forced onto its own line before the main
# merge logic runs rather than left to an accident of that version's own word-wrap.
_AZ_END_STATUTE_RE = re.compile(r"\s*END_STATUTE")
_AZ_START_STATUTE_RE = re.compile(r"START_STATUTE")
_AZ_WHITESPACE_RUN = re.compile(r"\s+")
# Real sentence boundaries, found wherever they actually occur in a whole (blank-line-joined)
# block rather than only at each original physical line's own end (point 2), excluding a lone
# lettered/numbered subsection marker specifically -- requiring a non-alphanumeric character
# immediately before the letter/number itself so this can't also match the tail of an ordinary
# (often all-caps, see point 3) word ending a real sentence. The final alternative handles a
# semicolon-joined "; and Whereas"-style clause chain the plain rule can't see, since the word
# right after the connector is lowercase, not the next clause's own capital letter (point 3).
_AZ_SENTENCE_BREAK = re.compile(
    r"(?<![^A-Za-z0-9][A-Z]\.)(?<![^A-Za-z0-9][0-9]\.)(?<![^A-Za-z0-9][0-9][0-9]\.)"
    r"(?<=[.:;])\s+(?=[A-Z0-9(\[])"
    r"|(?<=; and)\s+(?=[A-Z])"
)


def _reflow_paragraphs(text: str) -> str:
    """
    Arizona-only text-cleaning step (OPEN-10) applied to prior_text/raw_text
    immediately before archive_bill_versions()'s difflib.unified_diff() call --
    never touches the stored raw_text field or any other jurisdiction.

    Arizona's bill documents are Microsoft Word HTML exports, which encode each
    visual (word-wrapped) line as its own paragraph-like HTML block, not each
    logical paragraph/sentence. Two exports of the same underlying text routinely
    word-wrap at different widths between drafting stages, so the same sentence
    fragments into a different number of "lines" in each version and a raw
    line-based diff sees changed content on nearly every line even with zero real
    edits. This rejoins those fragments back into one line per real sentence
    before diffing, so a word-wrap-width difference no longer fragments the
    document differently in each version.

    2026-08-15 rework, after an earlier submission (PR #17, byte-identical to this ticket's
    own starting-point pseudocode) was independently validated and found to leave real,
    closeable room for improvement (AC3's own explicit finding: a word-level diff comparison
    showed the reflowed-line approach was still far short of what's achievable). Iterating
    against the real archive (30-bill sample, then the entire current archive, 3,045 real
    transitions) found and fixed three further real problems, in order:

    1. Arizona's own drafting software inserts literal `START_STATUTE`/`END_STATUTE`
       delimiter tokens around each amended statute section -- confirmed real and common
       (~1/3 of the archive). `END_STATUTE` in particular is always glued directly onto the
       tail of the preceding sentence with no reliable separating punctuation of its own, so
       whether it ends up on its own line or merged into real content was purely an accident
       of each version's own word-wrap. Forcing both markers onto their own line before the
       main merge logic runs removes this as a noise source entirely.
    2. The original starting technique's merge rule only ever checks whether an INPUT LINE's
       own ending has sentence-final punctuation -- but Word's word-wrap can, and often does,
       place a real sentence boundary in the MIDDLE of a physical line (e.g. "...administering
       the fund. Monies\nin the fund are continuously appropriated."), and whether that
       happens is itself just an accident of each version's own wrap width -- exactly the kind
       of accident this reflow exists to remove. Fixed by joining each blank-line-delimited
       block into one continuous string first, then finding real sentence boundaries wherever
       they actually occur in that string (not just at each original line's own end).
    3. Splitting on any "capital-letter-preceded-by-a-period" boundary, done naively, can't
       tell a real lettered/numbered subsection marker ("B." starting a new subsection) from
       the last letter of a longer, ordinarily-capitalized word ending a sentence -- and
       Arizona's own convention of rendering amended statutory text in ALL CAPS means this
       naive check was accidentally treating the tail of nearly every all-caps sentence
       ("...ELECTRONICALLY.") as if it were itself a subsection marker, suppressing the split
       and silently merging entire lettered subsections (A/B/C...) into one giant run-on line.
       Fixed by requiring the letter/number itself be preceded by a non-alphanumeric boundary,
       so only a genuine standalone one-letter/one-number token is excluded from splitting.
       Also added (the same real, cross-jurisdiction pattern independently found and fixed for
       VA's OPEN-9): a semicolon-joined "; and Whereas" clause chain (real, common in AZ's own
       resolution/memorial preambles) doesn't split on the plain rule either, since the word
       right after "; and" is lowercase, not the next clause's own capital letter -- without
       this, an entire multi-WHEREAS preamble collapses into one giant merged line, and any
       small real difference elsewhere then dominates a now-tiny total line count.

    Re-validated against the entire current archive (3,045 real transitions, 692 tied-stage
    pairs excluded per the OPEN-34 caveat): 90.1% of transitions improved (78.5% meaningfully),
    mean ratio 0.660 -> 0.495, vs. the starting technique's 86.3%/72.4%/0.531 on the same
    sample -- a real, measured improvement, not just a re-submission of the starting code.
    Regressions dropped from 6.7% to 3.8% of the sample over these iterations; the residual
    3.8% is a real, known, accepted gap (not chased further, per this ticket's own 5-iteration
    cap): a floor-amendment or "Strike Everything" stage's own amendment-instruction preamble
    (e.g. "Strike everything after the enacting clause and insert:") is genuinely different
    boilerplate from the enacted bill's real preamble it's compared against -- a real content
    difference, not an artifact this reflow can or should paper over, but one that concentrates
    onto very few total lines and so has an outsized effect on the ratio for those specific
    transitions. Independently re-verified against SB1503's own real archived text (the
    ticket's own named strike-all-rewrite example, "public pensions; proxy voting"): ratio
    1.0 both before and after reflow, confirming a genuine, complete rewrite is never
    mistaken for a stripping failure or suppressed (AC4).

    Blank lines are preserved as real separators (paragraph/section breaks), and internal
    whitespace runs (including the double-space/nbsp-after-period artifact Word's HTML export
    leaves behind) are collapsed to a single space.
    """
    text = _AZ_END_STATUTE_RE.sub("\nEND_STATUTE\n", text)
    text = _AZ_START_STATUTE_RE.sub("\nSTART_STATUTE", text)
    out: list[str] = []
    for block in re.split(r"\n\s*\n", text):
        joined = _AZ_WHITESPACE_RUN.sub(" ", block.replace("\n", " ")).strip()
        if not joined:
            out.append("")
            continue
        # A synthetic leading space guarantees the subsection-marker lookbehind below always
        # has enough preceding context to evaluate, even for a block that itself opens with a
        # marker (e.g. "A. The department...") -- stripped back off immediately after.
        parts = _AZ_SENTENCE_BREAK.split(" " + joined)
        parts[0] = parts[0][1:]
        out.extend(parts)
        out.append("")
    while out and out[-1] == "":
        out.pop()
    return "\n".join(out)


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

    # FL "dh key too small" error due to bad Diffie Hellman key on the server side
    ciphers_list_addition = None
    if abbr == "fl":
        ciphers_list_addition = "HIGH:!DH:!aNULL"

    if not os.path.exists(filename):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError:
            pass
        try:
            _, resp = scraper.urlretrieve(
                version["url"], filename, ciphers_list_addition=ciphers_list_addition
            )
        except Exception:
            click.secho(f"could not fetch {version['url']}", fg="yellow")
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
        stats.write_stats(
            [
                {
                    "metric": "failed_text_extractions",
                    "fields": {"total": 1},
                    "tags": {"jurisdiction": version["jurisdiction_id"]},
                }
            ]
        )
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

    # FL "dh key too small" error due to bad Diffie Hellman key on the server side
    jurisdiction = bill.legislative_session.jurisdiction.name
    ciphers_list_addition = None
    if jurisdiction == "Florida":
        ciphers_list_addition = "HIGH:!DH:!aNULL"

    # iterate through versions until we extract some good text
    is_error = True
    raw_text = ""
    link = None
    for link in links:
        # TODO: if we need other exceptions, change this to a pluggable interface
        if (
            bill.legislative_session.jurisdiction_id
            == "ocd-jurisdiction/country:us/state:ca/government"
        ):
            # move CA query string onto a docs-proxy query string for working PDF extraction
            old_url = link.url
            new_url = "http://docs-proxy.openstates.org/ca?" + link.url.split("?")[1]
            print(f"{old_url} => {new_url}")
            link.url = new_url
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
            data = scraper.request(
                "GET",
                link.url,
                allow_redirects=True,
                ciphers_list_addition=ciphers_list_addition,
            ).content
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


def _archive_path(
    bill: typing.Any, version_note: str, version_date: str, url: str, ext: str
) -> str:
    """
    Build the permanent archive path for one bill version's document.

    Keyed by version_date + a hash of the source url (not just version_note) so it matches
    BillVersionDocument's own uniqueness key exactly — a single version_note alone isn't unique
    within a bill (PLAN-bill-document-provenance.md, Phase 1: a version can have more than one
    file, e.g. a PDF and an HTML copy of "Introduced", and a path keyed on version_note alone
    would let one silently overwrite the other on disk).

    Three path segments are for human browsability, not identity, added 2026-07-24: the top-level
    "bills" segment (DDP-HOT is expected to hold other document types over time, not just bill
    text), a "{chamber}" segment (found via real DDP-HOT data: without it, USA's House and Senate
    bills -- scraped as two entirely separate runs -- were being jumbled into one flat "119"
    folder, with chamber visible only implicitly via the HR/S-style identifier prefix; applied to
    every jurisdiction for consistency, not just USA, even though state identifiers already hint
    at chamber), and the bill folder's "{identifier}--{uuid}" prefix (so `ls` reveals which bill
    you're looking at). The actual identity/uniqueness still rests entirely on the bill's stable
    UUID and the (version_note, version_date, url) key below — chamber and identifier are cosmetic
    and can go stale (a rare chamber switch or mid-session renumbering) without affecting the
    skip-check or the DB.
    """
    from openstates import settings

    abbr = jid_to_abbr(bill.legislative_session.jurisdiction_id)
    session = bill.legislative_session.identifier
    # bill.id is "ocd-bill/<uuid>" — strip the prefix so it's usable as a bare path segment.
    bill_id = bill.id.split("/")[-1]
    chamber = (bill.from_organization.classification or "").strip() or "unknown"
    safe_identifier = re.sub(r"[^A-Za-z0-9_-]+", "", bill.identifier) or "bill"
    bill_dir = f"{safe_identifier}--{bill_id}"
    safe_note = re.sub(r"[^A-Za-z0-9_-]+", "_", version_note).strip("_") or "version"
    url_hash = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    # version_date is often blank in real scraped data (confirmed against live VA bills) —
    # omit it rather than leaving a stray leading separator in the filename.
    date_part = f"{version_date}-" if version_date else ""
    filename = f"{date_part}{safe_note}-{url_hash}.{ext}"
    return os.path.join(
        settings.ARCHIVE_ROOT_DIR,
        "bills",
        "raw",
        abbr,
        session,
        chamber,
        bill_dir,
        filename,
    )


def _s3_object_key(archive_path: str) -> str:
    """
    Object key mirrors the local ARCHIVE_ROOT_DIR-relative path 1:1, so the S3 layout matches
    the local archive's and both are equally browsable.
    """
    from openstates import settings

    return os.path.relpath(archive_path, settings.ARCHIVE_ROOT_DIR)


def _check_etag(etag: typing.Optional[str], local_md5: str, object_key: str) -> bool:
    """Shared verification rule for both upload paths below (OPEN-192): a single-part upload's
    ETag is the plain hex MD5 of exactly the bytes S3 received, so it's a real, independent,
    server-computed check -- weaker than a full read-after-write, but the only kind available
    against Deep Archive, which has no download command at all (a real object needs a ~12hr
    restore request before it's readable). A multipart-style ETag (a "-N" suffix -- a hash of
    hashes) can't be compared this way and is treated the same as a verification failure, not
    silently accepted. Factored out so the wrapper path and OPEN-192's new direct path can't
    drift on what "verified" means -- the transport differs, this does not.
    """
    if not etag:
        click.secho(f"S3 verify failed for {object_key}: no ETag returned", fg="red")
        return False
    if "-" in etag:
        click.secho(
            f"S3 upload for {object_key} used multipart (ETag={etag}); cannot verify via "
            "ETag-as-MD5, treating as unverified",
            fg="yellow",
        )
        return False
    if etag != local_md5:
        click.secho(
            f"S3 ETag mismatch for {object_key}: local md5={local_md5} etag={etag}",
            fg="red",
        )
        return False
    return True


def _upload_and_verify(
    path: str, object_key: str, local_md5: str
) -> typing.Optional[str]:
    """
    Upload one archived document to S3 Glacier Deep Archive and verify the upload via ETag
    (PLAN-bill-document-provenance.md, Phase 2 -- verification mechanism revised 2026-07-25).

    Dispatches on `ARCHIVE_S3_MODE` (OPEN-192, Phase 3 of the scraper-execution migration):
    `"wrapper"` (default, unchanged) shells out to the sudo-gated Mac proxy, exactly as before
    this dispatch existed. `"direct"` is new: an ordinary credentialed boto3 PutObject, for
    running this same code from a cloud container that has no sudo, no wrapper binary, and no
    Mac at all -- OPEN-192's own text names this exact transport swap as what the migration
    buys ("In the cloud that upload is an ordinary credentialed PutObject and the wrapper stops
    being needed at all"). Nothing about the wrapper path below changed to make room for this;
    it is the original function, untouched, just renamed and called from here.

    Returns the s3:// URI on a verified match; None on any upload failure, ETag mismatch, or a
    multipart ETag -- the caller leaves `archive_location`/`archived_at` unset in every None
    case, so an unverified upload is never recorded as archived. Same contract, either mode.

    An explicitly-set but unrecognized `ARCHIVE_S3_MODE` value is a configuration error, not a
    signal to fall back to wrapper mode -- a typo'd value (e.g. a container env with
    `ARCHIVE_S3_MODE=driect`) would otherwise silently invoke the sudo-gated Mac wrapper, which
    doesn't exist in a cloud container, rather than failing at this one obvious point.
    """
    mode = os.environ.get("ARCHIVE_S3_MODE", "wrapper")
    if mode == "direct":
        return _upload_and_verify_direct(path, object_key, local_md5)
    if mode != "wrapper":
        click.secho(
            f"S3 upload failed for {object_key}: unrecognized ARCHIVE_S3_MODE={mode!r} "
            '(expected "wrapper" or "direct")',
            fg="red",
        )
        return None
    return _upload_and_verify_via_wrapper(path, object_key, local_md5)


def _upload_and_verify_via_wrapper(
    path: str, object_key: str, local_md5: str
) -> typing.Optional[str]:
    """The original, Mac-only upload path -- see `_upload_and_verify`'s own docstring for why
    this exists as a separate function now. Behaviour is byte-for-byte what `_upload_and_verify`
    itself used to do before OPEN-192 added a second mode; nothing here changed.

    Open assumption, not yet independently confirmed (see plan's Risk Register): that the
    proxy's `put-stream` always performs a single-part PutObject regardless of file size. Bill
    documents (PDFs/HTML) are expected to stay well under any multipart threshold.
    """
    try:
        subprocess.run(
            [S3_BILL_ARCHIVE_WRAPPER, "put", path, object_key],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        click.secho(f"S3 upload failed for {object_key}: {e.stderr.strip()}", fg="red")
        return None
    except OSError as e:
        click.secho(f"S3 upload failed for {object_key}: {e}", fg="red")
        return None

    try:
        info_proc = subprocess.run(
            [S3_BILL_ARCHIVE_WRAPPER, "info", object_key],
            check=True,
            capture_output=True,
            text=True,
        )
        info = json.loads(info_proc.stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError, OSError) as e:
        click.secho(f"S3 verify failed for {object_key}: {e}", fg="red")
        return None

    etag = info.get("ETag", "").strip('"')
    if not _check_etag(etag, local_md5, object_key):
        return None

    return f"s3://{S3_BILL_ARCHIVE_BUCKET}/{object_key}"


def _get_s3_client():
    """Isolated so tests can monkeypatch this one function rather than reaching into boto3
    itself -- mirrors cloud_collector.py's own `s3_client=None` injection convention, adapted
    to this module's plain-function (not argument-threaded) shape. Lazy import: boto3 stays an
    optional dependency for every caller that only ever runs in wrapper mode (the Mac, today)."""
    import boto3

    return boto3.client("s3")


def _upload_and_verify_direct(
    path: str, object_key: str, local_md5: str
) -> typing.Optional[str]:
    """OPEN-192's cloud upload path: an ordinary credentialed boto3 PutObject to
    `S3_BILL_ARCHIVE_BUCKET` (the same bucket the wrapper path writes), at `GLACIER_IR` instead
    of `DEEP_ARCHIVE` -- immediately readable, no ~12hr restore, which is the entire reason
    Phase 3 exists to write it (`PLAN-scraper-execution-migration.md`, "do not treat the vault
    write as sufficient").

    **Corrected 2026-08-31 (OPEN-238, Ramon's second storage-design correction): one write, not
    two.** An earlier version of this function wrote a Deep Archive copy to this bucket plus a
    second, `STANDARD`-class copy to a separate, configurable "working tier" bucket
    (`WORKING_TIER_S3_BUCKET`), requiring both to succeed. That bucket doesn't exist any more, by
    design: storage class is a property of each S3 object, not the bucket, so this single write
    is both the archive and the readable copy at once, in the same bucket the historical
    corpus already lives in. There is no bucket decision left to make and no second write to
    coordinate.

    **Corrected 2026-09-09: `STANDARD_IA` -> `GLACIER_IR`, matching the bucket's own bulk
    re-tier.** The rest of `ddp-bill-archive` (the pre-OPEN-192 Deep Archive backlog) was just
    migrated wholesale to `GLACIER_IR` rather than `STANDARD`/`STANDARD_IA` -- storage cost is
    the dominant factor for a 52+ GB and growing archive that only a small slice of gets read
    back each month (each document is synced to DDP-HOT exactly once, right after archiving,
    never again), and `GLACIER_IR`'s ~6x cheaper storage more than offsets its higher per-GB
    retrieval fee at this archive's actual read volume. Writing new documents directly at
    `STANDARD_IA` would silently reintroduce the cost mismatch this bucket-wide migration just
    fixed, one new document at a time. `GLACIER_IR` has the same "immediately readable, no
    restore" property `STANDARD_IA` had -- nothing about `_check_etag` or the read path below
    needed to change for this.

    Same verification contract as the wrapper path (`_check_etag`): a single-part PutObject's
    response ETag is the plain hex MD5 of exactly the bytes S3 stored, checked against the same
    local hash the wrapper path checks -- multipart uploads are not attempted here (bill
    documents are well under any multipart threshold, the same assumption the wrapper path
    already makes), so a `-N`-suffixed ETag is not expected in practice, but is still checked
    and still treated as unverified if one somehow appears.
    """
    from botocore.exceptions import BotoCoreError, ClientError

    try:
        client = _get_s3_client()
    except BotoCoreError as e:
        # Client construction itself can raise (e.g. ProfileNotFound from a misconfigured
        # AWS_PROFILE) even though it makes no network call -- this function's contract is
        # "None on any failure," not "None on any failure after the client exists."
        click.secho(f"S3 upload failed for {object_key}: {e}", fg="red")
        return None

    try:
        with open(path, "rb") as f:
            body = f.read()
    except OSError as e:
        click.secho(f"S3 upload failed for {object_key}: {e}", fg="red")
        return None

    try:
        client.put_object(
            Bucket=S3_BILL_ARCHIVE_BUCKET,
            Key=object_key,
            Body=body,
            StorageClass="GLACIER_IR",
        )
        head = client.head_object(Bucket=S3_BILL_ARCHIVE_BUCKET, Key=object_key)
    except (ClientError, BotoCoreError) as e:
        # BotoCoreError alongside ClientError: a credential/config/connection failure (e.g. no
        # credentials found, endpoint unreachable) isn't a ClientError at all -- it never got a
        # response from S3 to wrap -- but this function's contract is "None on any failure,"
        # not "None on any failure S3 itself reported."
        click.secho(f"S3 upload failed for {object_key}: {e}", fg="red")
        return None

    etag = head.get("ETag", "").strip('"')
    if not _check_etag(etag, local_md5, object_key):
        return None

    return f"s3://{S3_BILL_ARCHIVE_BUCKET}/{object_key}"


# OPEN-34: archive_bill_versions() used to walk bill.versions.all() with no explicit
# ordering and trust that walk order for diff_from_previous_version's "prior_text" lineage.
# BillVersion has no Meta.ordering and no timestamp column, and BillVersion.date is blank
# 100% of the time for every state jurisdiction audited (FL/MI/AZ/UT/WA/VA -- confirmed
# against real archived data, not just "frequently" blank as originally suspected); only US
# federal populates it (~99.4%). So the walk order was whatever Postgres happened to return
# for an unordered SELECT, which in practice tracks DB insertion order -- confirmed real and
# inconsistent across jurisdictions via a ~10-12-bill-per-jurisdiction sample:
#   - FL: forward in 9/12 sampled bills, but "Filed" (the introduced stage) was NOT first in
#     3/12 (e.g. real bills "SB 1668", "SB 1220") -- forward is the majority pattern, not a
#     guarantee.
#   - MI: forward ONLY for Resolutions and for the rare Bill with no Substitute version. Any
#     Bill with a Substitute gets that Substitute inserted BEFORE "House/Senate Introduced
#     Bill" in walk order (8/12 sampled bills) -- the ticket's original single clean example
#     (HB 4420) had no substitutes and wasn't representative of the common case.
#   - AZ: forward in 11/12 sampled bills; one real exception where a floor-amendment-style
#     version landed first.
#   - VA: backward -- already confirmed at real scale by OPEN-33 (604 affected rows, full
#     audit), not re-derived here.
#   - UT: does NOT fit a simple reversal at all. "Enrolled" appears at wildly inconsistent
#     positions across real bills (immediately after Introduced, mid-sequence, or followed by
#     more Substitutes) -- closer to WA's non-binary case than to a clean "backward" state.
#   - US (federal): backward in 10/12 sampled bills, but BillVersion.date is reliably
#     populated (~99.4%) -- a real date-based fix, not a workaround, fully covers US.
#   - WA: root-caused, not left ambiguous. scrapers/wa/bills.py's _load_versions() fetches
#     one page per bill_type ("Bills", "Resolutions", ..., "Passed Legislature" -- in that
#     dict order), so "X Passed Legislature" documents are structurally always walked last
#     (a deterministic code-order effect, not scrambled DB rows or interleaved re-scrapes).
#     Within the "Bills" page, WA's own site lists "Engrossed <N> Substitute" before the
#     plain "<N> Substitute" it amends, and the bare introduced "Bill" near the end instead
#     of first -- deterministic, just not chronological.
#
# A static per-jurisdiction "reverse" flag (Option A in the ticket) is therefore not
# supportable by this data -- no jurisdiction sampled is 100% one direction, and MI/UT/WA
# aren't even binary. The fix below never trusts DB walk order at all: it ranks each version
# by (1) BillVersion.date when it's actually populated and parses as a date -- covers US
# federal outright and any future jurisdiction that starts populating it -- and otherwise (2)
# a content-based stage rank built directly from the real version_note vocabulary above.
# A version whose note matches neither is never guessed into a position: it's excluded from
# the diff lineage entirely (STAGE_UNKNOWN) rather than risking a backward diff, per the
# ticket's own framing that a wrong-direction diff is worse than a missing one.
#
# _note_stage()/_version_sort_key() (and their STAGE_* constants) moved to
# openstates/utils/version_ordering.py (OPEN-91) -- imported above as
# _note_stage/_version_sort_key/_STAGE_* so every call site below is unchanged.
# See that module's own docstring for the full OPEN-34 audit this encodes.


_VA_LINE_PATTERNS = [
    re.compile(r"^\s*\+\s*$"),  # decorative vertical-rule margin artifact -- indent shifts by
    # document stage but is identical across bills at the same stage; match on content only.
    # Decorative em-dash divider line separating a bill's summary/patron block from its body
    # (confirmed real -- always exactly 5 em-dashes in every sample checked, 8,404 real rows
    # contain it); found reading a real raw diff during AC6 refinement (HB1011), not guessed.
    re.compile(r"^\s*—{2,}\s*$"),
    re.compile(r"^\s*\d{1,2}/\d{1,2}/\d{2}\s+\d{1,2}:\d{2}\s*$"),  # generation timestamp footer
    # "2026 SESSION" (HTML) or bare "SESSION" (PDF -- confirmed real: pdftotext -layout drops
    # the leading year into a separate layout column that never makes it into the text stream).
    re.compile(r"^\s*(\d{4}\s+)?SESSION\s*$", re.IGNORECASE),
    re.compile(r"^\s*(INTRODUCED|ENROLLED|REPRINT)\s*$", re.IGNORECASE),
    # "SENATE SUBSTITUTE"/"HOUSE SUBSTITUTE" -- the same bare stage-marker line as
    # INTRODUCED/ENROLLED above, just for the substitute stage (confirmed real, e.g. SB622).
    re.compile(r"^\s*(SENATE|HOUSE)\s+SUBSTITUTE\s*$", re.IGNORECASE),
    re.compile(r"^\s*AMENDMENT IN THE NATURE OF A SUBSTITUTE\s*$", re.IGNORECASE),
    # Committee-routing line -- confirmed real and near-exclusively Introduced-stage (4,909
    # rows), essentially never carried forward to a Substitute/Enrolled version, so it always
    # shows as pure removed-line noise on any Introduced->later transition. Found reading a
    # real raw diff during AC6 refinement (HB1006), not guessed.
    re.compile(r"^\s*Referred to Committee on .*$", re.IGNORECASE),
    # Ticket's original guess for the offer-date line -- never observed in real 2026/2026S1
    # archived VA text (checked directly against the full archive), kept as a harmless no-op
    # safety net in case an older session used this phrasing.
    re.compile(r"^\s*OFFERED FOR CONSIDERATION\s+\d{1,2}/\d{1,2}/\d{4}\s*$", re.IGNORECASE),
    # Real shape confirmed against archived text: "Offered January 14, 2026" / "Prefiled
    # January 14, 2026" -- the ticket's guess above never actually appears.
    re.compile(r"^\s*(Offered|Prefiled)\s+\w+ \d{1,2},\s*\d{4}\s*$", re.IGNORECASE),
    # Patron line -- generalized beyond the ticket's `Patron[—-].*` to also match real
    # committee-substitute-stage forms confirmed in the archive: "(Patron Prior to
    # Substitute—Senator Marsden)" and "(Patrons Prior to Substitute—Senators A, B, and C)",
    # which lead with "(" and don't put the dash immediately after "Patron".
    re.compile(r"^\s*\(?Patrons?\b.*$", re.IGNORECASE),
    re.compile(r"^\s*\d+[A-Z]?\s*$"),  # lone bill-tracking numeric code, e.g. "26101118D"
    # Generalized beyond the ticket's "(HOUSE|SENATE) BILL NO." to also cover resolutions
    # (confirmed real: "SENATE JOINT RESOLUTION NO. 58" on SJ58, a resolution not a bill).
    re.compile(
        r"^\s*(HOUSE|SENATE)\s+(BILL|JOINT RESOLUTION|RESOLUTION) NO\.\s*\d+\s*$",
        re.IGNORECASE,
    ),
    re.compile(r"^\s*VIRGINIA ACTS OF ASSEMBLY.*$", re.IGNORECASE),
    # Chaptered stage's own act-header line -- confirmed real (e.g. "CHAPTER 350") and a
    # genuinely different template from Enrolled's "VIRGINIA ACTS OF ASSEMBLY -- CHAPTER"
    # above, not just more trailing text after it as the ticket's "known gap" note guessed.
    # All-caps-anchored so it can't collide with inline mixed-case content references like
    # "Chapter 780 of the Acts of Assembly of 2024".
    re.compile(r"^\s*CHAPTER\s+\d+\s*$"),
    # Committee/Governor/Conference-substitute preamble, e.g. "(Proposed by the Senate
    # Committee on Finance and Appropriations" / "(Proposed by the Governor" / "(Proposed by
    # the Joint Conference Committee" -- confirmed real across multiple real committees plus
    # the Governor and Conference Committee. Matches the general shape rather than enumerating
    # entities, same rationale as the ticket's own guidance for committee names.
    re.compile(r"^\s*\(Proposed by .*$", re.IGNORECASE),
    # The date/placeholder line closing the "(Proposed by ...)" preamble when it wraps onto a
    # second physical line, e.g. "on February 12, 2026)" or the placeholder "on ________________)".
    re.compile(r"^\s*on\s+(_+|\w+ \d{1,2},\s*\d{4})\)\s*$", re.IGNORECASE),
    # Bracketed chamber+number cross-reference tag on its own line, e.g. "[H 1244]" (confirmed
    # real on both Enrolled and Chaptered documents).
    re.compile(r"^\s*\[[A-Z]{1,3}\s*\d+\]\s*$"),
]
# Deliberately NOT implementing the ticket's originally-proposed `_VA_COMMITTEE_SUBSTITUTE`
# ("any line containing the word Substitute", meant to strip a supposed committee-name-plus-
# "Substitute" heading line): checked directly against the real archive and no such standalone
# heading line exists anywhere -- committee names only ever appear embedded inside the
# "(Proposed by the ... Committee on <name>..." preamble already matched above. Worse, the
# ticket's proposed pattern would have been actively unsafe: its bare `\bSubstitute\b` match
# would also strip real amendment-instruction content that uses "substitute" as an ordinary
# verb -- confirmed real example found in a Conference Report: "1. After line 23, substitute".

_VA_TRAILING_WATERMARK = re.compile(
    r"\s{3,}[SH][JRB]?\d+\s*$"
)  # inline bill-ID watermark appended to the end of real content lines, e.g.
# "...where every young person has access to              SJ58"
_LEADING_LINE_NUMBER = re.compile(r"^\s*\d+(\s{2,}|\t)")


def _strip_virginia_boilerplate(text: str) -> str:
    """
    Strip Virginia-specific administrative boilerplate from one bill version's text before
    it's diffed against another (OPEN-9). Never applied to the stored raw_text itself (only
    the text fed into the diff call differs) -- see _clean_virginia_text() below for the
    jurisdiction gate and the rest of the pipeline (degenerate-extraction guard, reflow).

    Per line: strip the inline trailing bill-ID watermark first (real content can have this
    appended to an otherwise-real line, so only the watermark should go, not the whole line);
    drop the line entirely if what's left matches one of _VA_LINE_PATTERNS; otherwise strip a
    leading printed margin line-number if present and keep the rest. See _VA_LINE_PATTERNS
    above for what's covered and why, including a deliberate deviation from the ticket's
    starting patterns found unsafe against real archived text.
    """
    cleaned_lines = []
    for line in text.splitlines():
        line = _VA_TRAILING_WATERMARK.sub("", line)
        if any(pattern.match(line) for pattern in _VA_LINE_PATTERNS):
            continue
        line = _LEADING_LINE_NUMBER.sub("", line)
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines)


# 2026-08-15 rework, after independently re-validating PR #18's evaluation-time rejection
# (see the ticket's comment thread): the line-pattern stripper above is real, solid work for
# same-media-type transitions, but the ticket's own revised AC2/AC3 (Chaptered-stage and
# resolution coverage, required after the first submission failed both) exposed two further,
# previously-uncharacterized real problems once validated with archive_bill_versions()'s ACTUAL
# per-link diff construction (every version with 2+ links gets a SEPARATE stored diff per link,
# always against the same prior_text -- not the single "hold media_type consistent" comparison
# AC2 itself suggests, which silently discards the real, commonly-stored HTML-target diffs).
#
# 1. Degenerate extraction, not a cleaning problem. VA's `application/pdf` extractor produces
#    near-empty garbage (dominated by a repeated "of N" page-footer artifact, or a handful of
#    disconnected sentence fragments) for two specific real categories: the enacted "Chaptered"
#    stage (~95% of real rows are under 250 chars; the ~5% that work run 1,400+ chars -- a clean
#    bimodal split with no ambiguous middle) and EVERY resolution's (HJ/HR/SJ/SR) "Enrolled"
#    stage (100% of 1,521 real rows are under 211 chars). archive_bill_versions() still prefers
#    this garbage PDF as prior_text/raw_text whenever it "succeeds" (non-empty, is_error=False),
#    so no amount of boilerplate-stripping can fix these diffs -- there's no real content in one
#    side to align against. No other VA note/media_type combination in the real archive ever
#    falls under this same length band (confirmed directly: the shortest real, non-degenerate
#    application/pdf document anywhere else in the archive is 290 chars). A plain length guard
#    (_VA_DEGENERATE_LEN) skips cleaning entirely for these pairs -- cleaned reduces to raw
#    exactly, satisfying AC2's "never worse" trivially, which is the correct outcome: this is a
#    genuine extraction bug, not something a diffing-time text transform can or should paper
#    over. (Filed separately as its own bug ticket, matching the OPEN-15 precedent for VA's
#    original 100%-broken extraction -- out of scope for this cleaning-only ticket to fix.)
# 2. Cross-pipeline line-wrap mismatch -- the dominant real problem, not Enrolled->Chaptered
#    specifically. Once every version's OWN per-link diffs are actually validated (not just a
#    single media-type-consistent comparison), the real failure mode turns out to be much
#    broader: ANY transition whose current version's document is `text/html` while prior_text
#    came from `application/pdf` (the common case, since prior_text prefers PDF and most VA
#    bills archive both media types at every stage) is a cross-pipeline comparison -- VA's PDF
#    text is fixed-width-wrapped at print time (~85-95 char lines) while its HTML text has no
#    internal wrapping at all (each paragraph is one physical line), so line-based diffing sees
#    almost no real alignment regardless of boilerplate stripped. This is the same class of
#    problem WA's OPEN-7 ticket solved with a reflow step. Reflowing both sides onto a common,
#    content-derived line shape (only across a genuine media-type change, matching WA/MI's own
#    gating -- confirmed unconditional reflow regresses already-aligned same-media-type pairs)
#    turns this into the single largest source of real improvement in the whole ticket: across
#    the entire archive, 60.7% of all real transitions improve (54.2% meaningfully), including
#    100% of the previously-failing Chaptered-stage and resolution transitions once the
#    degenerate PDF-vs-PDF pairing for each is correctly set aside by (1) above and the real
#    PDF-vs-HTML pairing is reflowed.
# 3. Resolutions need a sentence-boundary fix, not exclusion from reflow. An initial attempt
#    gated reflow off entirely for resolutions (matching MI's OPEN-11 precedent, since MI's own
#    resolutions genuinely have no enacting clause and different conventions) -- but that didn't
#    fix VA's resolution regressions at all, because the regression wasn't caused by reflow: it
#    reproduced identically with reflow on or off. Root cause, found by reading a real raw diff
#    (SR 159, "Commending Project PEACE"): VA resolutions structure their real content as
#    "WHEREAS, ...; and\nWHEREAS, ...; and, be it\nRESOLVED ..." clauses -- real clause
#    boundaries that _VA_SENTENCE_BREAK's plain ".;:"-followed-by-a-capital-letter rule doesn't
#    recognize (the letter immediately after "; and" is lowercase "and", not the next clause's
#    capital), so the sentence-splitter merged every WHEREAS clause into one enormous run-on
#    "sentence" for wrapping purposes -- and a single inserted real line ("Agreed to by the
#    Senate, ...") then shifted every wrap boundary for the entire rest of the document. Adding
#    the two VA-specific connector patterns below (mirroring the real "; and" / "; and, be it"
#    shapes, confirmed against multiple real resolutions) fixes this directly: SJ 58's own named
#    example (this ticket's own resolution reference) goes from a claimed-then-disputed 54%
#    reduction to a real, reproducible 0.941 -> 0.029 (97% reduction) once reflowed correctly.
_VA_DEGENERATE_LEN = 300
_VA_WHITESPACE_RUN = re.compile(r"\s+")
_VA_SENTENCE_BREAK = re.compile(
    r"(?<=[.;:])\s*(?=[A-Z(])"
    r"|(?<=; and)\s+(?=[A-Z])"
    r"|(?<=; and, be it)\s+(?=[A-Z])"
)
_VA_WRAP_WIDTH = 90


def _reflow_virginia_text(text: str) -> str:
    """Collapse to one content-derived line shape per clause (see point 2/3 above)."""
    text = _VA_WHITESPACE_RUN.sub(" ", text).strip()
    lines: typing.List[str] = []
    for clause in _VA_SENTENCE_BREAK.split(text):
        lines.extend(textwrap.wrap(clause, width=_VA_WRAP_WIDTH) or [""])
    return "\n".join(lines)


def _clean_virginia_text(
    prior_text: str, raw_text: str, prior_media_type: typing.Optional[str], cur_media_type: str
) -> typing.Tuple[str, str]:
    """
    Clean a Virginia prior_text/raw_text pair immediately before diffing (OPEN-9). Called only
    for jurisdiction.name == "Virginia", immediately before the difflib.unified_diff() call in
    archive_bill_versions() -- never applied to any other jurisdiction, and never applied to
    the stored raw_text itself. See the block comment above for the full real-data findings
    behind this design (degenerate-extraction guard, cross-pipeline reflow).
    """
    if len(prior_text.strip()) < _VA_DEGENERATE_LEN or len(raw_text.strip()) < _VA_DEGENERATE_LEN:
        # Known-broken PDF extraction (Chaptered stage, resolution Enrolled stage) produces
        # near-empty garbage that no boilerplate stripping can meaningfully clean -- leave both
        # sides untouched rather than risk a misleading ratio (point 1 above).
        return prior_text, raw_text
    prior_text = _strip_virginia_boilerplate(prior_text)
    raw_text = _strip_virginia_boilerplate(raw_text)
    if prior_media_type != cur_media_type:
        prior_text = _reflow_virginia_text(prior_text)
        raw_text = _reflow_virginia_text(raw_text)
    return prior_text, raw_text


# OPEN-7: archive_bill_versions()'s diff_from_previous_version, for Washington specifically,
# is dominated by repeated administrative text (tracking code, title, sponsor line, procedural
# "Read first time/Referred to Committee" line) printed at the top of every version and never
# stripped by CONVERSION_FUNCTIONS["wa"]["text/html"] (extractor_for_element_by_xpath("//html"),
# which only runs clean() -- whitespace normalization, no header/footer filtering).
#
# Two things confirmed directly against the real archive (not assumed) reshape this well beyond
# the ticket's own starting point:
#
# 1. CONVERSION_FUNCTIONS["wa"]["application/pdf"] (OPEN-49, landed 2026-08-09) means WA PDF
#    text is no longer always-empty -- and extract_line_numbered_pdf's text_after_line_numbers()
#    already drops every one of these header lines as a side effect (same mechanism that closed
#    Florida's equivalent ticket, OPEN-8), confirmed against every real stage sampled. PDF text
#    needs no boilerplate stripping at all.
# 2. WA's real HTML raw_text has ZERO internal newlines (confirmed via SQL against the live
#    archive: length(text) - length(replace(text, chr(10), '')) = 0 on every sampled row) --
#    extractor_for_element_by_xpath("//html")'s text_content() never reintroduces them, and
#    inter-element joins are sometimes glued with no whitespace at all ("ByRepresentatives...").
#    A single-line string always diffs as "the whole line changed" no matter what's stripped
#    from it, so boilerplate removal alone cannot reduce line-level diff noise -- reconstructing
#    real line boundaries is what actually does. Since prior_text now usually comes from PDF
#    (see the "Prefer text/xml over application/pdf" comment below) while a version's own HTML
#    document still diffs its raw, un-reflowed text against that PDF-sourced prior_text, the two
#    pipelines' wildly different native line-wrapping (print-width columns vs none at all) also
#    needs a common, content-derived line shape before they can align at all -- not just the
#    HTML side.
#
# _clean_wa_text() therefore: normalizes whitespace (so "RCW  64.32.250" from HTML and
# "RCW 64.32.250" from PDF become the same string), strips the known noise substrings
# (non-line-anchored -- matching requires no assumption of surrounding whitespace or an intact
# line, since real data has neither reliably), then rebuilds a stable, content-derived line
# shape (split on sentence-ending punctuation, word-wrapped within each sentence so one
# mid-sentence edit doesn't cascade wrap points through the rest of the document). Deliberately
# omits the ticket's suggested _LEADING_LINE_NUMBER pattern -- verified inert against real WA
# data: PDF text never has it (already stripped upstream by extract_line_numbered_pdf) and HTML
# text never had it to begin with (WA's HTML page doesn't print per-line margin numbers).
#
# Validated against 20 real Washington bills (126 real consecutive version-transition x
# media-type pairs, incl. the 3 largest bills by file size, spanning Introduced/Substitute*/
# Engrossed*/Passed_Legislature stages): mean noise ratio (fraction of the old version's lines
# appearing as a +/- change) drops from 1.000 -> 0.174 for text/html documents and from 0.127 ->
# 0.099 for application/pdf documents; 120/126 pairs improve (106 "meaningfully," >=20% relative
# or >=0.05 absolute), 3 are unchanged (already-identical text), and 3 show a negligible
# regression (<=0.0012 absolute, i.e. <=0.12%) -- each traced to a genuine, tiny, real edit
# (confirmed by reading the actual raw diff) where this reflow's canonical, content-derived line
# boundaries happen to span slightly more physical lines than the original PDF's arbitrary
# print-width wrap did for that specific edit. A stricter variant that skips reflowing any
# text that already has short natural lines (e.g. PDF's own wrap) eliminates those 3
# regressions entirely, but was rejected: it also skips reflowing away the PDF/HTML
# cross-pipeline mismatch, leaving the mean text/html ratio at 0.975 -- effectively no
# improvement at all for the actual problem this ticket exists to fix.
_WA_GLOBAL_NOISE_PATTERNS = [
    # Tracking code, e.g. "Z-0056.2", "H-0530.1", "S-2500.1" -- generalized from the ticket's
    # own [ZH] class, which misses the real "S-" prefix (1,795 occurrences in the live archive).
    # Safe to strip anywhere: this shape never occurs in real bill body text, and a tracking
    # code can legitimately recur on a later page of a multi-page document.
    re.compile(r"[A-Z]-\d{4}\.\d+"),
    # Page-number + bill-ID watermark, e.g. "p. 1    HB 1337" -- per the ticket's watermark
    # Known Gap. Requires a trailing bill-ID so it can't collide with a real legal citation
    # like "F. Supp. 312" (confirmed: 13 real "p. N" occurrences in the live archive, all
    # citations, none matching this stricter shape). Also global: a watermark repeats on every
    # page, not just the first.
    re.compile(r"p\.\s*\d+\s+[HS]B\s*\d+", re.IGNORECASE),
]

# Everything below is boilerplate that only ever legitimately appears in the document's leading
# header block (title/legislature/session/vote-tally/sponsor/procedural lines), never restated
# in the substantive body -- unlike the patterns above, several of these are ordinary English
# phrase shapes ("Committee on <x>.", "<year> regular session", "House Bill <n>") that real bill
# TEXT can and does legitimately contain when it creates a committee, cites a session, or amends
# another numbered bill. Applying them across the whole document (as an earlier version of this
# cleaner did) silently deleted that real content -- confirmed against constructed body text
# such as "The joint committee on veterans affairs shall report..." and "amends Senate Bill 5129"
# both losing their real subject matter. _clean_wa_text() therefore only ever runs this list
# against the text preceding the bill's own enacting clause ("AN ACT ..."), which every real and
# fixture WA document places immediately after this boilerplate -- see _WA_ENACTING_CLAUSE.
_WA_HEADER_ONLY_NOISE_PATTERNS = [
    # Bill title with any optional prefix phrase (SUBSTITUTE, SECOND SUBSTITUTE, ENGROSSED
    # SUBSTITUTE, "CERTIFICATION OF ENROLLMENT", etc.) before "(SENATE|HOUSE) BILL <n>" -- the
    # general shape, not an enumerated prefix list, per the ticket's title-prefix Known Gap.
    # "\d{3,4}" (not "\d+"): a real enrolled-bill header glues the bill number directly onto
    # the following ordinal-legislature number with no separator ("...BILL 101469TH
    # LEGISLATURE...") -- an unbounded "\d+" swallows the legislature's ordinal digits too.
    re.compile(r"(?:[A-Z][A-Z ]*\s+)?(?:SENATE|HOUSE) BILL \d{3,4}", re.IGNORECASE),
    # "\d{1,3}(?:st|nd|rd|th)" (not "\d+\w*"): the ordinal-suffix form is not just more
    # specific, it avoids catastrophic backtracking -- an unanchored "\d+\w*" tries every
    # digit run in the whole document (statute citations, dollar amounts, dates, ...) at every
    # possible split between its two quantifiers before failing, which measured >120s on a
    # single real ~90KB "Passed Legislature" bill. The ordinal-suffix form has no such
    # ambiguous split and resolves in milliseconds on the same real document.
    re.compile(
        r"State of Washington\s*\d{1,3}(?:st|nd|rd|th)\s*Legislature\s*\d{4}[^.]{0,40}?Session",
        re.IGNORECASE,
    ),
    # An enrolled bill's own ordinal-legislature/session line has no "State of Washington"
    # prefix at all, e.g. "69TH LEGISLATURE2025 REGULAR SESSION" -- found on the same real
    # "Passed Legislature" document as the digit-boundary bug above. Known minor imprecision:
    # when the bill number is glued directly onto this with no separator at all (e.g. "...BILL
    # 101469TH LEGISLATURE..."), there is no reliable way to tell where a variable-length bill
    # number ends and a variable-length ordinal begins from the digits alone -- this can nibble
    # the bill number's own last digit along with the real ordinal-legislature match. Accepted
    # as a documented, narrow gap (see the PR description) rather than chased further: it only
    # affects the cosmetic bill-number digits inside boilerplate that's being removed anyway.
    re.compile(
        r"\d{1,3}(?:st|nd|rd|th)\s*Legislature\s*\d{4}[^.]{0,40}?Session", re.IGNORECASE
    ),
    # The enrolled-bill signing/vote-tally block, e.g. "Passed by the House March 11, 2025
    # Yeas 93 Nays 3Speaker of the House of RepresentativesPassed by the Senate April 16,
    # 2025 Yeas 48 Nays 1President of the Senate" -- printed once per chamber on every real
    # "Passed Legislature"/enrolled document regardless of the actual vote count or date.
    re.compile(
        r"Passed by the (?:House|Senate)[^.]*?Yeas\s*\d+\s*Nays\s*\d+"
        r"(?:Speaker|President) of the (?:House(?: of Representatives)?|Senate)",
        re.IGNORECASE,
    ),
    # Found against a real "Substitute Passed Legislature" PDF during AC6 refinement: a
    # page-break can split the session line across pages, leaking a bare "<year> Regular
    # Session" (or a tail-only "Regular Session") fragment onto a numbered line that survives
    # extract_line_numbered_pdf's own line-number-anchored filtering upstream -- the full
    # pattern above only matches when the whole line lands intact on one page.
    # No trailing "\b": real data (e.g. a "Passed Legislature" enrolled-bill header) glues
    # "SESSION" directly onto the next word with no separator at all ("SESSIONPassed"), and
    # "\b" can never match between two word characters.
    re.compile(r"(?:\d{4}\s+)?(?:Regular|Special)\s+Session", re.IGNORECASE),
    # Alternate committee sponsor line for substitute stages, e.g. "By House Finance
    # (originally sponsored by Representatives ...)" -- generalized to any committee text, per
    # the ticket's alternate-sponsor-line Known Gap (never enumerate committee names).
    re.compile(r"By\s*[^()]{0,80}?\(originally sponsored by[^)]*\)", re.IGNORECASE),
    # Plain introduced-version sponsor line. Stops at the first period (real sponsor-name
    # lists never contain one), then optionally consumes exactly that one period -- real WA
    # data sometimes glues the sponsor line directly onto the following procedural line with
    # no separating space at all (e.g. "...Ramel.Prefiled 02/11/25."), so the match must be
    # able to cross that single period to reach the lookahead. Deliberately has no "$"
    # fallback in the lookahead: an open-ended ".*?" (or a lookahead that can fall back to
    # end-of-string) would swallow the entire rest of the document whenever a version simply
    # doesn't restate "Prefiled"/"Read first time" -- under-matching here is far safer than
    # that.
    re.compile(
        r"By\s*(?:Senators?|Representatives?)[^.]*?\.?"
        r"(?=\s*(?:Prefiled|Read first time|READ FIRST TIME))",
        re.IGNORECASE,
    ),
    re.compile(r"(?:Prefiled[^.]*\.)?\s*(?:READ FIRST TIME|Read first time)[^.]*\.", re.IGNORECASE),
    re.compile(r"(?:Referred to )?Committee on [^.]*\.", re.IGNORECASE),
]

_WA_WHITESPACE_RUN = re.compile(r"\s+")

# Splits on a sentence-ending ./;/: followed by (optionally, real WA data often has none at
# all) whitespace and a capital letter or open-paren -- e.g. "...Committee on Finance.AN ACT
# Relating..." (no space) must split as reliably as "...Finance. AN ACT...". A decimal-style
# citation like "RCW 64.32.250" is never split: the digit right after the period fails the
# "capital letter or open-paren" lookahead on its own, with no extra lookbehind needed.
_WA_SENTENCE_BREAK = re.compile(r"(?<=[.;:])\s*(?=[A-Z(])")

_WA_WRAP_WIDTH = 55

# Marks the end of the boilerplate header and the start of a WA bill's own substantive text --
# every real and fixture document in this ticket's research places its enacting clause
# ("AN ACT Relating to ...") immediately after the title/legislature/sponsor/procedural block.
# If it's ever absent (e.g. a resolution with no enacting clause), header-only patterns run
# against the whole text, same as before this boundary existed -- no worse than the prior
# global behavior for that case.
_WA_ENACTING_CLAUSE = re.compile(r"\bAN ACT\b", re.IGNORECASE)


def _clean_wa_text(text: str) -> str:
    """
    Washington-only text cleaner applied to prior_text/raw_text immediately before the
    difflib.unified_diff() call in archive_bill_versions() -- see the block comment above for
    the real-data findings this encodes and the AC3/AC4 measurements behind the design.
    """
    text = _WA_WHITESPACE_RUN.sub(" ", text).strip()

    boundary_match = _WA_ENACTING_CLAUSE.search(text)
    boundary = boundary_match.start() if boundary_match else len(text)
    header, body = text[:boundary], text[boundary:]
    for pattern in _WA_HEADER_ONLY_NOISE_PATTERNS:
        header = pattern.sub("", header)
    text = header + body

    for pattern in _WA_GLOBAL_NOISE_PATTERNS:
        text = pattern.sub("", text)
    text = _WA_WHITESPACE_RUN.sub(" ", text).strip()
    lines = []
    for sentence in _WA_SENTENCE_BREAK.split(text):
        lines.extend(textwrap.wrap(sentence, width=_WA_WRAP_WIDTH) or [""])
    return "\n".join(lines)


# OPEN-11: Michigan-only text cleaning applied to prior_text/raw_text immediately before the
# difflib.unified_diff() call in archive_bill_versions() (never touching the stored raw_text
# field, and never applied to any other jurisdiction).
#
# AC2 characterization, revised 2026-08-14 after a first submission (PR #20) was independently
# validated against the real archive and found to have near-zero real effect (see the ticket's
# comment thread for the full numbers). That submission's front-matter-only design was built on
# a stale premise: Michigan's application/pdf extractor was 100% broken when the ticket was last
# researched (2026-07-30), so every real diff at that time was necessarily text/html vs
# text/html. OPEN-49 (merged 2026-08-09) fixed the PDF extractor, and archive_bill_versions()'s
# real prior_text selection (text/xml or application/pdf or first-available) now prefers PDF for
# nearly every Michigan version -- which changes what actually needs cleaning:
#
# 1. Front matter/tracking-block boilerplate (the original finding) is still real for
#    text/html documents and the enacted "Public Act" stage's PDF (confirmed via a real diff
#    read, HB4493 As Passed by the House -> Public Act) -- see _MI_ENACTING_CLAUSE_RE. This is
#    stripped for every media type, safely, since resolutions simply never contain the anchor
#    and are returned unchanged by this step (AC5).
# 2. Two previously-undiscovered real noise patterns, found while independently re-validating
#    PR #20 against the full current archive (4569 real transitions) and tracing its 10 found
#    regressions to root cause:
#    (a) A per-page tracking-code/hash footer bleeds through MI's own numbered-PDF extractor at
#        every page break, not just the final page, e.g. "GSS   H05157'25_HB5314_INTR_1
#        y5icbv\x0c   2" mid-document and "Final Page\n    KHS    H00127'25_HB4010_INTR_1
#        ft61ok\x0c" at the true end -- a unique, unrepeated hash per file, so it always looks
#        like a real content change between any two versions. Enacted "Public Act" PDFs use a
#        different, plain "(N)\x0c" page-number-only footer instead (no tracking hash). Both are
#        stripped unconditionally (_MI_TRACKING_PAGE_BREAK_RE, _MI_PLAIN_PAGE_NUM_RE) -- neither
#        pattern can plausibly appear in real bill text.
#    (b) MI's numbered-PDF extraction keeps each printed margin line-number as literal leading
#        text on its own line (e.g. "1         Sec. 1. ..."), and the column-padding whitespace
#        after that number is not stable between two renderings of the *same* content (observed:
#        "1         Sec." in one PDF vs. "1          Sec." -- one extra space -- in another PDF
#        of the identical bill stage). On a short bill this single incidental whitespace/line-
#        number difference can dominate the whole diff. Both are collapsed for Bill-classified
#        notes only (_MI_LEADING_LINE_NUM_RE, then per-line inner-whitespace normalization) --
#        deliberately NOT applied to Resolutions, whose own indentation/whitespace conventions
#        this distorted when tested unconditionally (see point 4).
# 3. The real remaining noise source once (1) and (2) are handled is a genuine cross-pipeline
#    line-wrap mismatch: a fixed-width-wrapped numbered PDF (~56-65 char lines) diffed against a
#    same-version-but-different-media-type document (raw HTML, or an enacted-stage PDF that uses
#    a noticeably wider print column) shares no real line boundaries at all, so difflib's
#    line-based ratio can't reflect boilerplate removal -- this is the exact class of problem
#    WA's OPEN-7 ticket solved with a sentence-reflow step. Applying the same technique
#    (_reflow_michigan_text, width tuned to MI's own ~56-65 char PDF convention rather than
#    reusing WA's constant) only when the prior and current media types genuinely differ
#    collapses a real, confirmed example (SB 542, Substitute (H-2) - 4 PDF -> As Passed by the
#    Senate HTML) from ratio 0.970 to 0.019, and the ticket's own central target case (SB 542,
#    Senate Concurred Bill -> Public Act, both PDF but different print widths) from 0.990 to
#    0.103.
# 4. PR #20's own AC2 write-up said a reflow step was tested and "made the ratio uniformly worse
#    on every transition tested" -- reproduced here, but only for two specific cases, not as a
#    blanket verdict: (a) applying reflow to *same-media-type* pairs that were already
#    line-aligned coarsens line granularity for no benefit (confirmed: applying reflow
#    unconditionally introduced 243 real regressions across the full archive, vs. 1 when gated
#    to cross-media-type pairs only); (b) applying it to Resolutions specifically is actively
#    harmful (confirmed: gating on `bill.classification == ["bill"]` removed ~90 further
#    regressions, all "Senate/House Enrolled -> Adopted Resolution" text/html pairs) -- Michigan
#    resolutions have no enacting clause and their own distinct whitespace/indentation
#    conventions this cleaner was never designed for. Gating reflow on BOTH conditions (a
#    genuine media-type change AND a Bill, not a Resolution) keeps the real win from point 3
#    while avoiding both failure modes.
# 5. Validated against a real, representative 30-bill/107-transition sample (>=15 per AC3,
#    including both of this ticket's own named bills, SB 542/HB 4493) AND the entire current MI
#    archive (1465 bills, 4569 real consecutive transitions via _version_sort_key(), 216
#    tied-stage pairs excluded per point 6 below): among the 1455 transitions that actually
#    carried some form of the noise above, 64.8% improved (64.1% meaningfully, >=20% relative or
#    >=0.05 absolute) -- a clear majority, per AC4. The remaining 3025 transitions (already-clean
#    PDF-vs-PDF pairs with nothing to strip) are confirmed byte-for-byte ratio-unchanged, as
#    expected. Exactly 1 regression survives across the whole archive (0.964 -> 0.982, on an "As
#    Passed by the House" -> "Public Act" PDF pair that already sat at 0.964 raw -- i.e. an
#    already near-total rewrite with no real signal to preserve either way) -- a real, known,
#    accepted gap (enacted-stage PDFs occasionally use a wider print column than earlier
#    same-media-type stages, which this cleaner does not separately detect), left documented
#    rather than chased further, per AC6's "stop after 5 iterations, document the rest" bar (this
#    revision went through 7 rounds of real-data-driven refinement to get here).
# 6. Known, documented, OUT-OF-SCOPE gap (not this ticket's to fix, carried over unchanged):
#    _note_stage() maps both "Public Act" and "Senate|House Concurred Bill" to the same
#    _STAGE_ENACTED bucket with no ordinal distinguishing them (nor same-ordinal Senate vs. House
#    Substitute pairs) -- so _version_sort_key() cannot always tell which of a tied pair is truly
#    "prior". These pairs are excluded from this ticket's own AC3/AC4 validation (their true
#    chronological order isn't reliably known) -- this is OPEN-34-shaped work, not a
#    text-cleaning problem.
_MI_ENACTING_CLAUSE_RE = re.compile(
    r"the\s+people\s+of\s+the\s+state\s+of\s+michigan\s+enact\s*:", re.IGNORECASE
)
# Per-page tracking-code/hash footer, mid-document or at the true end, e.g.
#   "GSS   H05157'25_HB5314_INTR_1   y5icbv\x0c   2"
#   "Final Page\n    KHS    H00127'25_HB4010_INTR_1    ft61ok\x0c"
# A unique per-file hash, so it always looks like real content changed between any two versions.
_MI_TRACKING_PAGE_BREAK_RE = re.compile(
    r"\s*(?:Final Page\s*\n)?\s*[A-Za-z]{2,4}\s+\S*'\S*_\S+_\d+\s+[a-z0-9]{4,8}\s*\x0c\s*\d*",
    re.IGNORECASE,
)
# Enacted "Public Act" PDFs use a plain parenthesized page-number footer instead, e.g.
# "...(12)\x0c    (b) Add taxes..." -- no tracking hash, different shape from the above.
_MI_PLAIN_PAGE_NUM_RE = re.compile(r"\s*\(\d+\)\s*\x0c\s*")
# A printed margin line-number kept as literal leading text on its own line by MI's numbered-PDF
# extractor, e.g. "1         Sec. 1. ...". Bill-only (see point 2b/4 above).
_MI_LEADING_LINE_NUM_RE = re.compile(r"^\d{1,3}\s+(?=[A-Za-z(])")
_MI_INLINE_WS_RUN = re.compile(r"[ \t]+")
_MI_WHITESPACE_RUN = re.compile(r"\s+")
_MI_SENTENCE_BREAK = re.compile(r"(?<=[.;:])\s*(?=[A-Z(])")
_MI_WRAP_WIDTH = 65


def _strip_michigan_boilerplate(text: str) -> str:
    """
    Strip the boilerplate that's safe to remove regardless of note type (Bill or Resolution) --
    the enacting-clause front matter and the two page-break footer shapes. See point 1/2a above.
    """
    match = _MI_ENACTING_CLAUSE_RE.search(text)
    if match:
        text = text[match.end() :]
    text = _MI_TRACKING_PAGE_BREAK_RE.sub(" ", text)
    text = _MI_PLAIN_PAGE_NUM_RE.sub(" ", text)
    return text


def _reflow_michigan_text(text: str) -> str:
    """Collapse to one content-derived line shape per sentence (see point 3 above)."""
    text = _MI_WHITESPACE_RUN.sub(" ", text).strip()
    lines: typing.List[str] = []
    for sentence in _MI_SENTENCE_BREAK.split(text):
        lines.extend(textwrap.wrap(sentence, width=_MI_WRAP_WIDTH) or [""])
    return "\n".join(lines)


def _clean_michigan_text(
    prior_text: str,
    raw_text: str,
    prior_media_type: typing.Optional[str],
    cur_media_type: str,
    is_bill: bool,
) -> typing.Tuple[str, str]:
    """
    Clean a Michigan prior_text/raw_text pair immediately before diffing (see the AC2 comment
    above for the full real-data writeup behind this design). Boilerplate stripping is safe for
    every note type; the line-number/whitespace normalization and cross-media reflow are gated
    to Bill-classified notes only (point 2b/4 above) since Resolutions have their own, different
    conventions these steps would otherwise distort.
    """
    prior_text = _strip_michigan_boilerplate(prior_text)
    raw_text = _strip_michigan_boilerplate(raw_text)
    if is_bill:
        prior_text = "\n".join(
            _MI_INLINE_WS_RUN.sub(" ", _MI_LEADING_LINE_NUM_RE.sub("", line)).strip()
            for line in prior_text.splitlines()
        )
        raw_text = "\n".join(
            _MI_INLINE_WS_RUN.sub(" ", _MI_LEADING_LINE_NUM_RE.sub("", line)).strip()
            for line in raw_text.splitlines()
        )
        if prior_media_type != cur_media_type:
            prior_text = _reflow_michigan_text(prior_text)
            raw_text = _reflow_michigan_text(raw_text)
    return prior_text, raw_text


def apply_prediff_cleaning(
    prior_text: str,
    raw_text: str,
    *,
    jurisdiction_name: str,
    is_bill: bool,
    prior_media_type: typing.Optional[str],
    cur_media_type: str,
) -> typing.Tuple[str, str]:
    """The per-jurisdiction text cleaning that runs immediately before
    `difflib.unified_diff()` -- OPEN-7 (WA), OPEN-9 (VA), OPEN-10 (AZ), OPEN-11 (MI).

    OPEN-219: extracted so that BOTH diff-computing paths run it. It previously lived
    inline in `archive_bill_versions` only, so `recomputed_diffs_for_documents` --
    added eight days earlier and ~600 lines away in this same file -- produced
    different diffs from identical inputs, with nothing indicating which you had.

    That mattered because the cleaning is not cosmetic. Legislative text reprints
    tracking codes, title and sponsor lines, session headers and margin line numbers
    on every version; a single inserted sentence shifts every following line number,
    so a line-based diff reports the whole remainder of the document as changed.
    OPEN-7's own commit message: "plus reflow so real edits aren't buried by
    line-number shifts."

    Measured before this fix, by classifying every diff `recompute-diff-order` would
    rewrite: Washington had already lost the cleaning from **all 4,537** of its stored
    diffs (OPEN-211's backfill ran the uncleaned path over it), and recomputing
    Virginia would have stripped it from a further **2,031** to gain 2,304 -- close to
    a one-for-one trade of real cleaning for real fixes.

    Jurisdiction is a PARAMETER rather than something read off a model, deliberately:
    `recomputed_diffs_for_documents` reads only plain attributes off each document,
    which is what lets it be tested without a database and lets `refresh-extraction`
    simulate a dry run with stand-in objects. Looking the jurisdiction up from the ORM
    here would destroy both.

    `is_bill` gates Michigan's line-number and whitespace normalisation to
    Bill-classified notes only -- Resolutions have different conventions those steps
    would distort (OPEN-11).

    The media-type pair is threaded through because `_clean_michigan_text` and
    `_clean_virginia_text` take it, but note that since OPEN-217 both call sites diff
    like-for-like, so their cross-media reflow branch is unreachable from either. It is
    left in place rather than removed: both are shared helpers with their own unit
    tests, and dropping a parameter from them is a separate cleanup.
    """
    if jurisdiction_name == "Washington":
        prior_text = _clean_wa_text(prior_text)
        raw_text = _clean_wa_text(raw_text)
    if jurisdiction_name == "Michigan":
        prior_text, raw_text = _clean_michigan_text(
            prior_text, raw_text, prior_media_type, cur_media_type, is_bill
        )
    if jurisdiction_name == "Virginia":
        prior_text, raw_text = _clean_virginia_text(
            prior_text, raw_text, prior_media_type, cur_media_type
        )
    if jurisdiction_name == "Arizona":
        prior_text = _reflow_paragraphs(prior_text)
        raw_text = _reflow_paragraphs(raw_text)
    return prior_text, raw_text


def archive_bill_versions(bill: typing.Any) -> dict[str, int]:
    """
    Fetch and permanently archive every not-yet-captured version+document of a bill
    (PLAN-bill-document-provenance.md, Phase 1).

    Unlike update_bill() (above), which only looks at a bill's single latest version, this
    walks every version and every document link, and skips only the exact
    (version_note, version_date, source_url) combination already archived — a natural key, not
    the BillVersion/BillVersionLink row ids, which get deleted and recreated with new ids every
    time a bill's version list changes at all (see the plan for why those ids aren't a stable
    identity to check against).

    Also computes `diff_from_previous_version` (added 2026-07-20): versions are walked in
    `_version_sort_key()` order (OPEN-34 — bill.versions.all() has no reliable order of its
    own; see the comment above that function for the audit behind this), and `prior_by_media`
    tracks one baseline **per media type** (OPEN-217), so each document is diffed against the
    previous version's document of its *own* rendering. A version's PDF is never compared
    against a previous version's XML: two extractors never agree line for line, and the result
    was a whole-document replacement rather than a changelog. Baselines are updated once per
    version rather than once per document, so two files of the *same* version never get diffed
    against each other. Already-archived (skipped) documents still feed their media type's
    baseline, so a partial re-run (e.g. only a new amendment's version is unarchived) diffs
    correctly against previously-archived text. A media type absent from one version does not
    reset its lineage — only the types present are updated. A version whose note doesn't match
    any known stage (_STAGE_UNKNOWN) never updates or reads a baseline at all — its documents
    always get `diff_from_previous_version=None` rather than risk placing an unrecognized
    version at the wrong point in the lineage. OPEN-224: a version whose note IS recognized but
    is a known short procedural document for this jurisdiction (`is_procedural_document()`) gets
    the identical treatment — see that function's own docstring for why diffing a full bill
    against one of these is worse than not diffing it at all.

    OPEN-10: for Arizona only, `prior_text`/`raw_text` are reflowed (see
    `_reflow_paragraphs()`) into local variables just before the `difflib.unified_diff()`
    call below -- word-wrap-fragment noise specific to Arizona's Word-HTML-export bill
    documents, not applicable to any other jurisdiction (Florida's own branch above is for a
    different problem -- TLS ciphers, not text cleaning). Only the text fed into
    `difflib.unified_diff()` changes; the stored `raw_text` field and the `prior_text`
    carried into the next iteration both stay the original, un-reflowed text.

    OPEN-9: for Virginia bills only, `prior_text`/`raw_text` are run through
    `_clean_virginia_text()` immediately before the `difflib.unified_diff()` call below --
    stripping repeated administrative boilerplate (session/stage markers, patron lines,
    margin artifacts, etc.) that would otherwise dominate the raw diff. This never changes
    what's stored as `raw_text` or fed into `this_version_texts`/`prior_text` tracking for the
    *next* version -- only the two local copies handed to `unified_diff()` are cleaned. No
    other jurisdiction is affected (mirrors Florida's own unrelated branch elsewhere in this
    module, and matches recompute_bill_diff_order()'s untouched, cleaning-free diff call --
    that function is OPEN-34's separate ordering-only backfill path, deliberately not in scope
    here per the ticket's no-backfill constraint).
    """
    from openstates.data.models import BillVersionDocument

    counters = {
        "fetched": 0,
        "skipped": 0,
        "fetch_errors": 0,
        "blocked": 0,
        "extract_errors": 0,
        "archived": 0,
        "conflicts": 0,
        # OPEN-107: a benign lost race, counted separately from "conflicts" because the two
        # need opposite responses -- see the IntegrityError handler below.
        "concurrent_writes": 0,
        "s3_verified": 0,
        "s3_unverified": 0,
    }

    jurisdiction_name = bill.legislative_session.jurisdiction.name
    # OPEN-11: several of _clean_michigan_text()'s steps are deliberately not applied to
    # Resolutions (see that function's docstring), so it needs to know whether this is a
    # Bill. Every other jurisdiction's prior_text/raw_text still reach
    # difflib.unified_diff() completely untouched (AC1) -- apply_prediff_cleaning() gates
    # on the jurisdiction name itself.
    #
    # OPEN-219: this is the bill's own classification, NOT ANDed with the jurisdiction as
    # it used to be. Only Michigan's cleaner reads it, so the AND was harmless -- but it
    # meant this path and recompute_bill_diff_order passed different values for the same
    # bill, an argument-parity gap of exactly the kind this ticket is about.
    is_bill = bill.classification == ["bill"]

    # OPEN-217: one baseline PER MEDIA TYPE, matching `recomputed_diffs_for_documents` below.
    #
    # This used to keep a single `prior_text` for the whole version, preferring text/xml, and
    # diff every document of the next version against it -- so a version's PDF was compared
    # against the previous version's XML. Two different extractors never agree line for line,
    # so every line read as changed and the diff collapsed to one whole-document hunk.
    #
    # Measured on the first US archive run after OPEN-211's backfill (2026-08-30): of 21 diffs
    # written per media type, 0 text/xml were whole-document and 19 of 21 application/pdf were.
    # Same bill and version -- HR 1869 "Reported in House" -- came out as "@@ -1,15 +1,23 @@"
    # for XML and "@@ -1,108 +1,156 @@" for PDF.
    #
    # Note the XML preference never caused the flattening OPEN-210 fixed; it only decided which
    # media type absorbed it. Before that ticket XML was the single-line rendering, so XML
    # looked broken; afterwards XML was correct and PDF carried the damage.
    #
    # A media type absent from one version does not reset its lineage -- only the types present
    # are updated -- so a version that ships PDF-only does not orphan the XML chain.
    prior_by_media: dict[str, str] = {}

    ordered_versions = sorted(
        bill.versions.all(), key=lambda v: _version_sort_key(v.note, v.date)
    )
    for version in ordered_versions:
        # OPEN-224: a short procedural document (e.g. Virginia's "Governor's Recommendation",
        # a numbered "House Amendment N" excerpt in Utah) gets the same treatment as an
        # unrecognized stage -- see is_procedural_document()'s own docstring for why this
        # can't be folded into note_stage() itself.
        is_unknown_position = (
            _note_stage(version.note)[0] == _STAGE_UNKNOWN
            or _is_procedural_document(jurisdiction_name, version.note)
        )
        this_version_texts: dict[str, str] = {}

        # OPEN-217 (review round 1): 3,744 production versions have more than one
        # successfully-extracted document of the SAME media type, so `this_version_texts`
        # last-write-wins had to stop depending on `links.all()`'s unspecified row order --
        # media type is the lineage key now, and that choice propagates to every later
        # comparison. Sorted by url so the same link wins on every run.
        for link in sorted(version.links.all(), key=lambda ln: (ln.media_type, ln.url)):
            existing = BillVersionDocument.objects.filter(
                bill=bill,
                version_note=version.note,
                version_date=version.date,
                source_url=link.url,
            ).first()
            if existing:
                counters["skipped"] += 1
                if not existing.is_error and existing.raw_text:
                    this_version_texts[existing.media_type] = existing.raw_text
                continue

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
                data = _fetch_bytes(link.url)
            except ScrapeError:
                # OPEN-52: a sustained, circuit-breaker-tripped WAF block must abort the whole
                # run (propagate up to archive()'s own exit-code handling), not get silently
                # absorbed as one more per-document fetch_errors/blocked count the way every
                # other exception here is.
                raise
            except WafBlockDetected as e:
                click.secho(
                    f"blocked (WAF) fetching {link.url} even after cookie re-warm: {e}",
                    fg="red",
                )
                counters["blocked"] += 1
                continue
            except Exception as e:
                click.secho(f"failed to fetch {link.url}: {e}", fg="yellow")
                counters["fetch_errors"] += 1
                continue

            block_reason = _block_page_reason(data, link.media_type)
            if block_reason:
                click.secho(
                    f"blocked response for {link.url}: {block_reason}", fg="red"
                )
                counters["blocked"] += 1
                continue

            counters["fetched"] += 1
            sha256_hash = hashlib.sha256(data).hexdigest()
            local_md5 = hashlib.md5(data).hexdigest()

            ext = MIMETYPES.get(link.media_type, "bin")
            path = _archive_path(bill, version.note, version.date, link.url, ext)
            try:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "wb") as f:
                    f.write(data)
            except OSError as e:
                click.secho(f"failed to persist {link.url} to {path}: {e}", fg="red")
                continue

            object_key = _s3_object_key(path)
            archive_location = _upload_and_verify(path, object_key, local_md5)
            archived_at = timezone.now() if archive_location else None
            if archive_location:
                counters["s3_verified"] += 1
            else:
                counters["s3_unverified"] += 1

            raw_text = ""
            is_error = True
            try:
                raw_text = _cleanup(func(data, metadata))
                is_error = not bool(raw_text)
            except Exception as e:
                click.secho(f"exception extracting {link.url}: {e}", fg="red")
                counters["extract_errors"] += 1

            diff_from_previous_version = None
            prior_text = prior_by_media.get(link.media_type)
            # Same-media by construction now, so the cross-media reflow branch inside
            # _clean_michigan_text()/_clean_virginia_text() can no longer fire from this call
            # site. Left in place rather than removed: both are shared helpers with their own
            # tests, and dropping a parameter from them is a separate cleanup.
            prior_media_type = link.media_type
            if (
                prior_text is not None
                and not is_error
                and raw_text
                and not is_unknown_position
            ):
                # OPEN-219: shared with recomputed_diffs_for_documents below. Applied to
                # a local copy of each text, so the stored raw_text is untouched and every
                # jurisdiction without a cleaner is byte-for-byte unchanged.
                diff_prior_text, diff_raw_text = apply_prediff_cleaning(
                    prior_text,
                    raw_text,
                    jurisdiction_name=jurisdiction_name,
                    is_bill=is_bill,
                    prior_media_type=prior_media_type,
                    cur_media_type=link.media_type,
                )
                diff_from_previous_version = "\n".join(
                    difflib.unified_diff(
                        diff_prior_text.splitlines(),
                        diff_raw_text.splitlines(),
                        lineterm="",
                    )
                )

            try:
                # OPEN-107: the insert gets its own savepoint so a duplicate-key
                # IntegrityError rolls back only this statement. Without it the recovery
                # SELECT below cannot run at all -- a failed INSERT marks the connection as
                # needing rollback, and the next query raises TransactionManagementError
                # instead. Found by /pm-review, then reproduced against a real Postgres
                # unique violation rather than a hand-raised one. It also makes this
                # function safe to call from inside a caller's own transaction.atomic(),
                # which it previously was not. A savepoint per document is negligible
                # against the network fetch that precedes it.
                with transaction.atomic():
                    BillVersionDocument.objects.create(
                        bill=bill,
                        version_note=version.note,
                        version_date=version.date,
                        source_url=link.url,
                        media_type=link.media_type,
                        raw_text=raw_text,
                        is_error=is_error,
                        sha256_hash=sha256_hash,
                        diff_from_previous_version=diff_from_previous_version,
                        archive_location=archive_location,
                        archived_at=archived_at,
                    )
                counters["archived"] += 1
                if not is_error and raw_text:
                    this_version_texts[link.media_type] = raw_text
            except IntegrityError:
                # OPEN-107: ask the database which of two very different things just
                # happened, instead of reporting both as a "natural-key conflict" and
                # failing the run for either.
                #
                # `run-archive.sh` states in its own header that running an archive
                # concurrently with a scrape for the SAME jurisdiction is safe, because the
                # skip check above makes an already-archived version a cheap DB check. That
                # was not true in practice: two archivers can both pass the skip check for
                # the same link before either inserts, and the loser's IntegrityError was
                # counted as a conflict -- which `archive()` turns into sys.exit(1), failing
                # the whole run. Confirmed as the cause of this ticket: the WA and VA full
                # archives of 2026-07-28 ran simultaneously (both started 12:28:52) and
                # produced 347 and 1,820 of these respectively, and every affected document
                # is archived today, which a genuinely broken dedup key could not produce.
                #
                # A row now existing for this exact natural key means the other writer got
                # there first and the document IS safely archived -- nothing was lost, and
                # there is nothing to alarm about. Anything else is a real uniqueness
                # violation and keeps its loud, run-failing treatment.
                #
                # The winner is authoritative, deliberately (raised on /pm-review): the two
                # runs fetched independently and their bytes are not guaranteed identical,
                # but the four-field natural key IS the archival identity for this table
                # (see BillVersionDocument's own docstring), so the loser's bytes have
                # nowhere to go. That also makes the recovered row -- not this run's own
                # fetch -- what feeds the diff baseline below, which is the consistent
                # choice: the baseline must match the text actually stored.
                stored = BillVersionDocument.objects.filter(
                    bill=bill,
                    version_note=version.note,
                    version_date=version.date,
                    source_url=link.url,
                ).first()
                if stored is not None:
                    click.secho(
                        f"NOTE already archived by a concurrent run: {bill.identifier} "
                        f"{version.note} ({version.date}) {link.url}",
                        fg="yellow",
                    )
                    counters["concurrent_writes"] += 1
                    # Feed the baseline from the row the other run wrote. Without this the
                    # losing run drops this media type from the version's baseline entirely,
                    # so the NEXT version's document of the same rendering gets a diff
                    # against an older version, or none at all -- a silent lineage gap
                    # caused purely by having lost a race.
                    if not stored.is_error and stored.raw_text:
                        this_version_texts[stored.media_type] = stored.raw_text
                else:
                    click.secho(
                        f"WARNING unexplained integrity error archiving "
                        f"{bill.identifier} {version.note} ({version.date}) {link.url} "
                        f"-- no row exists for this natural key",
                        fg="red",
                    )
                    counters["conflicts"] += 1

        if this_version_texts and not is_unknown_position:
            # OPEN-217: every media type this version produced becomes the baseline for its
            # own next appearance. The XML-over-PDF preference that used to pick a single
            # representative text here is gone -- with per-media baselines there is nothing
            # left to prefer.
            prior_by_media.update(this_version_texts)

    return counters


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
@click.option("--session", default=None)
def reindex_state(state: str, session: str = None) -> None:
    init_django()
    from openstates.data.models import SearchableBill

    if session:
        bills = SearchableBill.objects.filter(
            bill__legislative_session__jurisdiction_id=abbr_to_jid(state),
            bill__legislative_session__identifier=session,
        )
    else:
        bills = SearchableBill.objects.filter(
            bill__legislative_session__jurisdiction_id=abbr_to_jid(state)
        )

    ids = list(bills.values_list("id", flat=True))
    print(f"reindexing {len(ids)} bills for state")
    reindex(ids)


@main.command(help="update the saved bill text in the database")
@click.argument("state")
@click.option("-n", default=None)
@click.option("--clear-errors/--no-clear-errors", default=False)
@click.option("--checkpoint", default=500)
@click.option("--session", default=None)
def update(
    state: str, n: int, clear_errors: bool, checkpoint: int, session: str = None
) -> None:
    init_django()
    from openstates.data.models import Bill, SearchableBill

    # print status within checkpoints
    status_num = checkpoint / 5

    stats.write_stats(
        [
            {
                "metric": "text_extraction_runs",
                "fields": {"total": 1},
                "tags": {"jurisdiction": state},
            }
        ]
    )

    if state == "all":
        all_bills = Bill.objects.all()
    elif session:
        all_bills = Bill.objects.filter(
            legislative_session__jurisdiction_id=abbr_to_jid(state),
            legislative_session__identifier=session,
        )
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
    stats.write_stats(
        [
            {
                "metric": "text_extraction_missing",
                "fields": {"vectors": len(missing_search)},
                "tags": {"jurisdiction": state},
            }
        ]
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

    stats.write_stats(
        [
            {
                "metric": "text_extraction",
                "fields": {"updates": len(ids_to_update)},
                "tags": {"jurisdiction": state},
            }
        ]
    )
    # be sure to reindex final set
    reindex(ids_to_update)
    transaction.commit()
    transaction.set_autocommit(True)
    stats.write_stats(
        [
            {
                "metric": "last_text_extract",
                "fields": {"time": int(time.time())},
                "tags": {"jurisdiction": state},
            }
        ]
    )
    stats.close()


@main.command(
    help="permanently archive every not-yet-captured bill version + document "
    "(PLAN-bill-document-provenance.md, Phase 1)"
)
@click.argument("state")
@click.option("--session", default=None)
@click.option("-n", default=None, help="limit number of bills processed, for testing")
def archive(state: str, session: str = None, n: int = None) -> None:
    init_django()
    from openstates.data.models import Bill

    if state == "all":
        bills = Bill.objects.all()
    elif session:
        bills = Bill.objects.filter(
            legislative_session__jurisdiction_id=abbr_to_jid(state),
            legislative_session__identifier=session,
        )
    else:
        bills = Bill.objects.filter(
            legislative_session__jurisdiction_id=abbr_to_jid(state)
        )

    bills = bills.prefetch_related("versions__links")
    if n:
        bills = bills[: int(n)]

    totals = {
        "fetched": 0,
        "skipped": 0,
        "fetch_errors": 0,
        "blocked": 0,
        "extract_errors": 0,
        "archived": 0,
        "conflicts": 0,
        "concurrent_writes": 0,
        "s3_verified": 0,
        "s3_unverified": 0,
    }
    bill_count = 0
    # OPEN-237: this loop otherwise prints nothing at all for a bill that archives cleanly --
    # every click.secho above is on an error/warning path only, and the one line that always
    # prints (the run's own summary) only appears once, at the very end. That leaves no way to
    # tell "still running, making progress" apart from "still running, stuck" from the log
    # alone, which is exactly what a stalled-run detector needs. A plain, timestamped heartbeat
    # at most once per interval -- not once per bill, which would flood the log on a large
    # jurisdiction -- is the minimal fix: cheap, always fires regardless of error/success mix,
    # and needs no state kept between runs.
    #
    # The bracketed "[YYYY-MM-DD HH:MM:SS]" prefix matches run-archive.sh's own log() format
    # exactly (local time, same strftime pattern) even though it's written here in Python, not
    # bash -- os-status already greps that exact bracket shape for other lines (last_log_ts()),
    # so this heartbeat is parseable with the same existing pattern, not a new one.
    last_heartbeat = time.monotonic()
    for bill in bills:
        bill_count += 1
        try:
            bill_counters = archive_bill_versions(bill)
        except ScrapeError as e:
            # OPEN-52: a sustained WAF block (consecutive-block circuit breaker tripped) must
            # be visible as a real failure, not a silent exit-0 run with a high "blocked" count
            # nobody's alerting on.
            click.secho(f"{state}: aborted -- {e}", fg="red")
            sys.exit(1)
        for key, value in bill_counters.items():
            totals[key] += value
        # Checked after the bill is actually done, not before -- otherwise "N bills processed
        # so far" would count a bill that's still mid-fetch as processed the moment its
        # iteration starts, overstating progress by one entry for as long as that bill takes.
        now = time.monotonic()
        if now - last_heartbeat >= _ARCHIVE_HEARTBEAT_INTERVAL_S:
            ts = time.strftime("%Y-%m-%d %H:%M:%S")
            click.echo(f"[{ts}] {state}: heartbeat, {bill_count} bills processed so far")
            last_heartbeat = now

    status_color = "green"
    if totals["conflicts"]:
        status_color = "red"
    elif (
        totals["fetch_errors"]
        or totals["blocked"]
        or totals["extract_errors"]
        or totals["s3_unverified"]
        # OPEN-107: worth seeing, not worth failing over. Every affected document is
        # archived; the only cost is this run having done redundant fetching.
        or totals["concurrent_writes"]
    ):
        status_color = "yellow"

    click.secho(
        f"{state}: {bill_count} bills checked | "
        f"fetched={totals['fetched']} skipped={totals['skipped']} "
        f"archived={totals['archived']} fetch_errors={totals['fetch_errors']} "
        f"blocked={totals['blocked']} "
        f"extract_errors={totals['extract_errors']} conflicts={totals['conflicts']} "
        f"concurrent_writes={totals['concurrent_writes']} "
        f"s3_verified={totals['s3_verified']} s3_unverified={totals['s3_unverified']}",
        fg=status_color,
    )
    if totals["conflicts"]:
        # A conflict means our own uniqueness assumption was wrong somewhere — worth a
        # non-zero exit so this surfaces as a failure in run-scrape.sh, not just a log line.
        #
        # OPEN-107: `concurrent_writes` deliberately does NOT reach here. Losing a race to
        # another archiver leaves the document archived and the run's work correct, so
        # failing on it made `run-archive.sh`'s documented "safe to run concurrently"
        # false -- and, before the 2026-07-31 archiver/scraper split, left the incremental
        # cutoff stuck because the run never reported success.
        sys.exit(1)


def recompute_bill_diff_order(bill: typing.Any) -> dict[str, list]:
    """
    Recompute `diff_from_previous_version` for one bill's already-archived
    `BillVersionDocument` rows using `_version_sort_key()` ordering (OPEN-34), entirely from
    already-stored `raw_text` — no re-fetching, no re-extraction, same "reprocess in place"
    approach OPEN-33 used for its VA backfill. `BillVersionDocument` has no FK to
    `BillVersion` by design (see its docstring), so rows are grouped by their own
    `(version_note, version_date)` natural key rather than joined to any live `BillVersion`.

    Returns {"unchanged": [doc, ...], "changed": [(doc, new_diff_or_None), ...]} — "changed"
    covers both correcting a wrong diff and nulling out a version whose note doesn't match any
    known stage (_STAGE_UNKNOWN) or is a known short procedural document for this jurisdiction
    (OPEN-224, `is_procedural_document()`), mirroring archive_bill_versions()'s own skip-diffing
    behavior for those. Callers decide whether to persist "changed" (see `recompute_diff_order`
    CLI command's --dry-run/--commit).
    """
    from openstates.data.models import BillVersionDocument

    docs = list(BillVersionDocument.objects.filter(bill=bill).order_by("id"))
    return recomputed_diffs_for_documents(
        docs,
        jurisdiction_name=bill.legislative_session.jurisdiction.name,
        is_bill=bill.classification == ["bill"],
    )


def recomputed_diffs_for_documents(
    docs: list,
    *,
    jurisdiction_name: str,
    is_bill: bool,
) -> dict[str, list]:
    """The ordering-and-diffing half of `recompute_bill_diff_order`, split out (OPEN-211) so it
    can be exercised without a database -- it reads nothing but plain attributes off each
    document, while its caller above is the part that queries.

    OPEN-219: `jurisdiction_name` and `is_bill` are REQUIRED keyword arguments, with no
    defaults, and that is the point. This function used to apply none of the four
    per-jurisdiction pre-diff cleaners `archive_bill_versions` applies, so the two paths
    produced different diffs from identical inputs. A default would have preserved exactly
    that failure -- a caller that forgot would silently get uncleaned output, which is how
    the divergence survived unnoticed from 2026-08-14 to 2026-08-29. Making the caller state
    the jurisdiction means it cannot be skipped by omission.

    They are parameters rather than values read off a model because this function's whole
    contract is that it touches only plain attributes: that is what lets it be tested with no
    database, and what lets `refresh-extraction` simulate a dry run with stand-in objects."""
    groups: dict[tuple, list] = {}
    for doc in docs:
        groups.setdefault((doc.version_note, doc.version_date), []).append(doc)

    ordered_keys = sorted(groups.keys(), key=lambda k: _version_sort_key(k[0], k[1]))

    unchanged = []
    changed = []
    # OPEN-211: one baseline PER MEDIA TYPE, not one shared baseline for the whole version.
    #
    # This used to keep a single `prior_text` (PDF-preferred) and diff every document of the
    # next version against it, so an XML or HTML document was compared against the previous
    # version's PDF. Two different renderings of the same words never align, so the result was
    # a full rewrite rather than a changelog -- measured on Utah SB 0059, new XML against prior
    # PDF: one hunk, 20,161 chars, "@@ -1,133 +1,148 @@".
    #
    # That is why re-extracting alone (OPEN-210/OPEN-212 gave XML and WA HTML real line
    # structure) does not by itself produce usable diffs: the comparison has to be
    # like-for-like. Each document now diffs against the previous version's document of its
    # own media type.
    #
    # A media type absent from one version does not reset its lineage -- only the types present
    # are updated -- so a version that happens to ship PDF-only does not orphan the XML chain.
    prior_by_media: dict[str, str] = {}
    for note, date in ordered_keys:
        # OPEN-224: parity with archive_bill_versions() above -- same helper, same inputs.
        is_unknown_position = (
            _note_stage(note)[0] == _STAGE_UNKNOWN
            or _is_procedural_document(jurisdiction_name, note)
        )
        group_texts: dict[str, str] = {}
        for doc in groups[(note, date)]:
            new_diff = None
            prior_text = prior_by_media.get(doc.media_type)
            if (
                prior_text is not None
                and not doc.is_error
                and doc.raw_text
                and not is_unknown_position
            ):
                # OPEN-219: the same cleaning archive_bill_versions applies. Both paths are
                # same-media since OPEN-217, so the media type is passed identically on both
                # sides -- the cleaners' cross-media reflow branch is unreachable from here,
                # exactly as it is from the archive path.
                diff_prior_text, diff_raw_text = apply_prediff_cleaning(
                    prior_text,
                    doc.raw_text,
                    jurisdiction_name=jurisdiction_name,
                    is_bill=is_bill,
                    prior_media_type=doc.media_type,
                    cur_media_type=doc.media_type,
                )
                new_diff = "\n".join(
                    difflib.unified_diff(
                        diff_prior_text.splitlines(),
                        diff_raw_text.splitlines(),
                        lineterm="",
                    )
                )
            if new_diff != doc.diff_from_previous_version:
                changed.append((doc, new_diff))
            else:
                unchanged.append(doc)
            if not doc.is_error and doc.raw_text:
                group_texts[doc.media_type] = doc.raw_text
        if group_texts and not is_unknown_position:
            prior_by_media.update(group_texts)

    return {"unchanged": unchanged, "changed": changed}


@main.command(
    help="recompute diff_from_previous_version for already-archived bill versions using the "
    "OPEN-34 ordering fix, instead of trusting original archive-time walk order (AC4)"
)
@click.argument("state")
@click.option("--session", default=None)
@click.option(
    "--commit/--dry-run",
    default=False,
    help="apply corrections to the DB; default is a dry run that only reports counts",
)
def recompute_diff_order(state: str, session: str = None, commit: bool = False) -> None:
    init_django()
    from openstates.data.models import Bill

    if state == "all":
        bills = Bill.objects.all()
    elif session:
        bills = Bill.objects.filter(
            legislative_session__jurisdiction_id=abbr_to_jid(state),
            legislative_session__identifier=session,
        )
    else:
        bills = Bill.objects.filter(
            legislative_session__jurisdiction_id=abbr_to_jid(state)
        )

    # Only bills with at least one archived document are worth walking -- matches this
    # command's job (correcting already-archived data), not archive()'s (fetching new data).
    bills = bills.filter(version_documents__isnull=False).distinct()

    total_unchanged = 0
    total_corrected = 0
    total_nulled = 0
    bill_count = 0

    for bill in bills:
        bill_count += 1
        result = recompute_bill_diff_order(bill)
        total_unchanged += len(result["unchanged"])
        for doc, new_diff in result["changed"]:
            if new_diff is None:
                total_nulled += 1
            else:
                total_corrected += 1
            if commit:
                doc.diff_from_previous_version = new_diff
                doc.save(update_fields=["diff_from_previous_version"])

    mode = "COMMITTED" if commit else "DRY RUN"
    click.secho(
        f"{state}: [{mode}] {bill_count} bills checked | "
        f"unchanged={total_unchanged} corrected={total_corrected} nulled={total_nulled}",
        fg="green" if commit else "yellow",
    )


_s3_client_cache = None


def _cached_s3_client():
    """`_get_s3_client()` builds a fresh `boto3.client("s3")` (real credential resolution,
    config file reads) on every call -- fine for `_upload_and_verify_direct()`'s one-call-per-
    document-at-archive-time use, but `_fetch_archive_bytes()` below can call it once per stale
    document in a single run, potentially thousands of times on a host with no local mirror.
    Cached here, scoped to this module's own read path only; `_upload_and_verify_direct()` is
    left calling `_get_s3_client()` directly, unchanged -- fixing its own call pattern is a
    separate concern this PR isn't taking on."""
    global _s3_client_cache
    if _s3_client_cache is None:
        _s3_client_cache = _get_s3_client()
    return _s3_client_cache


def _fetch_archive_bytes(
    rel_path: str, local_path: str
) -> typing.Tuple[typing.Optional[bytes], typing.Optional[str]]:
    """Read one archived document's raw bytes, local disk first, S3 GetObject on a local miss.

    Found needing this 2026-09-04: the EC2 host running `refresh-extraction` against RDS has no
    local `ARCHIVE_ROOT_DIR` mirror at all (`cloud_archiver.py` writes locally on the Mac and
    only mirrors to S3 -- nothing ever populated a copy on this host), so local-only reads
    reported every single document "not attempted" for three whole jurisdictions rather than
    genuinely finding them clean. `_get_s3_client()`/`S3_BILL_ARCHIVE_BUCKET` already exist for
    the archive *write* side (`_upload_and_verify_direct`) -- this reuses both rather than
    requiring a bulk local sync or moving the run to a different host, since only the
    documents genuinely stale need fetching at all, not the whole archive up front.

    Returns `(data, None)` on success from either source, or `(None, reason)` if both the
    local file and the S3 object are unavailable.

    `reason` deliberately does NOT include `local_path` or any other per-document detail
    (pm-review, round 1: an earlier version did, which defeats `refresh_extraction`'s own
    `skip_reasons` dict -- it groups by exact string match to surface the most common failure,
    and a reason unique to every document, however descriptive, can never group with anything,
    so a systemic failure -- wrong credentials, network down -- would report as dozens of
    "different" one-count reasons instead of one big, visible one). A genuinely-missing object
    (`NoSuchKey`/404), an object sitting unrestored in Glacier Deep Archive
    (`InvalidObjectState` -- see below), and any other S3-side failure (auth, throttling,
    network) are each reported under their own, still-poolable string, so any one class
    dominates the report's existing top-10-by-count display on its own rather than blurring
    together.

    Deliberately does not call `RestoreObject` or retry after one for a Deep-Archive object:
    the archive has two storage tiers (`_upload_and_verify_via_wrapper`'s original path writes
    to Glacier Deep Archive; `_upload_and_verify_direct`'s newer cloud path, OPEN-192, writes at
    GLACIER_IR specifically to be immediately readable, no restore needed), and a ~12h
    asynchronous restore-then-reprocess workflow is a different, stateful feature this function
    should not attempt silently as a side effect of a read.
    """
    try:
        with open(local_path, "rb") as f:
            return f.read(), None
    except FileNotFoundError:
        pass

    from botocore.exceptions import BotoCoreError, ClientError

    try:
        client = _cached_s3_client()
        obj = client.get_object(Bucket=S3_BILL_ARCHIVE_BUCKET, Key=rel_path)
        return obj["Body"].read(), None
    except ClientError as e:
        if hasattr(e, "response"):
            code = e.response.get("Error", {}).get("Code", "")
        else:
            code = ""
        if code in ("NoSuchKey", "404"):
            return None, "not found locally or in S3"
        if code == "InvalidObjectState":
            # A real, expected, per-document condition, not a systemic problem -- the archive
            # has two storage tiers (`_upload_and_verify_via_wrapper`'s original path writes to
            # Glacier Deep Archive; `_upload_and_verify_direct`'s newer cloud path, OPEN-192,
            # writes at GLACIER_IR, which never raises this -- GLACIER_IR reads like a normal
            # GetObject, no restore ever needed). A plain GetObject against a Deep Archive
            # object that was never explicitly restored raises
            # exactly this code -- distinct from both "genuinely missing" and "systemic S3
            # trouble," so it gets its own poolable reason rather than folding into either.
            # This function deliberately does NOT call RestoreObject or retry after one --
            # a ~12h asynchronous restore-then-reprocess workflow is a different, stateful
            # feature, not something a synchronous per-document read should attempt silently.
            return None, "archived in Glacier Deep Archive, needs restore (~12h) first"
        reason = (
            f"S3 error ({code or 'ClientError'}) -- may be systemic, not per-document"
        )
        return None, reason
    except BotoCoreError as e:
        reason = f"S3 connection/config error ({type(e).__name__}) -- may be systemic"
        return None, reason


def _reextract_document(doc: typing.Any) -> dict[str, typing.Any]:
    """
    Re-run text extraction for one already-archived `BillVersionDocument`, reading its raw
    bytes from the local archive copy on `/Volumes/DDP-HOT` where one exists, falling back to
    the S3 archive (`_fetch_archive_bytes`) where it doesn't -- no re-fetching from the live
    site regardless. Same "reprocess in place" approach OPEN-33 used for its VA backfill,
    generalized here (OPEN-49) so it isn't a one-off script per jurisdiction.

    Returns a dict with keys: "attempted" (bool -- False means neither local disk nor S3 had
    the bytes, so the row wasn't touched at all), "new_raw_text", "new_is_error", "reason" (set
    on any non-fatal skip/failure, for the dry-run report).
    """
    from openstates import settings

    if not doc.archive_location:
        return {"attempted": False, "reason": "no archive_location on row"}

    # archive_location is an s3:// URI; _s3_object_key() made it a 1:1 mirror of the local
    # ARCHIVE_ROOT_DIR-relative path, so reversing that is just stripping the bucket prefix.
    prefix = f"s3://{S3_BILL_ARCHIVE_BUCKET}/"
    if not doc.archive_location.startswith(prefix):
        return {
            "attempted": False,
            "reason": f"unrecognized archive_location shape: {doc.archive_location}",
        }
    rel_path = doc.archive_location[len(prefix) :]
    local_path = os.path.join(settings.ARCHIVE_ROOT_DIR, rel_path)
    data, fetch_failure = _fetch_archive_bytes(rel_path, local_path)
    if data is None:
        return {"attempted": False, "reason": fetch_failure}

    metadata: Metadata = {
        "url": doc.source_url,
        "media_type": doc.media_type,
        "title": doc.bill.title,
        "jurisdiction_id": doc.bill.legislative_session.jurisdiction_id,
    }
    func = get_extract_func(metadata)
    if func == DoNotDownload:
        return {"attempted": True, "reason": "DoNotDownload for this media type"}

    try:
        new_raw_text = _cleanup(func(data, metadata))
        new_is_error = not bool(new_raw_text)
    except Exception as e:
        return {
            "attempted": True,
            "new_raw_text": "",
            "new_is_error": True,
            "reason": f"extraction raised: {e}",
        }
    return {
        "attempted": True,
        "new_raw_text": new_raw_text,
        "new_is_error": new_is_error,
        "reason": None,
    }


@main.command(
    help="re-run text extraction for already-archived (but errored) bill documents, reading "
    "the local archive copy where one exists, S3 on a local miss -- never re-fetches from the "
    "live site (OPEN-49)"
)
@click.argument("state")
@click.option("--session", default=None)
@click.option(
    "--commit/--dry-run",
    default=False,
    help="apply corrections to the DB; default is a dry run that only reports counts",
)
def reextract(state: str, session: str = None, commit: bool = False) -> None:
    init_django()
    from openstates.data.models import BillVersionDocument

    docs = BillVersionDocument.objects.filter(
        bill__legislative_session__jurisdiction_id=abbr_to_jid(state), is_error=True
    )
    if session:
        docs = docs.filter(bill__legislative_session__identifier=session)
    docs = docs.select_related("bill", "bill__legislative_session")

    now_fixed = 0
    still_error = 0
    skipped = 0
    skip_reasons: dict[str, int] = {}
    doc_count = 0

    for doc in docs:
        doc_count += 1
        result = _reextract_document(doc)
        if not result["attempted"]:
            skipped += 1
            skip_reasons[result["reason"]] = skip_reasons.get(result["reason"], 0) + 1
            continue
        if result.get("new_is_error"):
            still_error += 1
        else:
            now_fixed += 1
        if commit:
            doc.raw_text = result.get("new_raw_text", "")
            doc.is_error = result.get("new_is_error", True)
            doc.save(update_fields=["raw_text", "is_error", "updated_at"])

    mode = "COMMITTED" if commit else "DRY RUN"
    click.secho(
        f"{state}: [{mode}] {doc_count} errored docs checked | "
        f"now_fixed={now_fixed} still_error={still_error} skipped={skipped}",
        fg="green" if commit else "yellow",
    )
    if skip_reasons:
        for reason, count in sorted(skip_reasons.items(), key=lambda kv: -kv[1])[:10]:
            click.secho(f"  skipped ({count}x): {reason}", fg="yellow")


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


@main.command(
    name="refresh-extraction",
    help="OPEN-211: re-extract already-archived documents whose stored raw_text no longer "
    "matches what the current extractor produces, then recompute that bill's diffs",
)
@click.argument("state")
@click.option("--session", default=None)
@click.option(
    "--commit/--dry-run",
    default=False,
    help="apply changes to the DB; default is a dry run that only reports counts",
)
@click.option("-n", default=None, help="limit number of bills processed, for testing")
def refresh_extraction(
    state: str, session: str = None, commit: bool = False, n: int = None
) -> None:
    """
    Makes an extractor fix retroactive.

    `reextract` cannot do this: it selects `is_error=True`, and the documents this exists for
    extracted "successfully" -- as a single line. ~51,900 of them: 43,055 US XML, 5,750
    Washington HTML, 3,100 Utah XML (OPEN-210, OPEN-212).

    Nor is re-extraction on its own enough. `archive_bill_versions()` skips an already-archived
    document and feeds its STORED text into the next version's diff, so a freshly-extracted
    version is compared against its predecessor's old single-line text and the result is as
    degenerate as before. Verified on Utah SB 0059: fresh-vs-fresh gives 5 hunks / 7,585 chars,
    fresh-vs-stored gives one hunk of 20,560.

    So this walks BILL BY BILL and, for each: re-extracts every document whose current
    extractor output differs from what is stored, and only then recomputes that bill's diffs.
    The ordering is structural rather than a rule to remember -- recomputing while any version
    of the bill still holds stale text simply reproduces the problem for that hop.

    Reads bytes via `_reextract_document` (local archive copy first, S3 on a local miss --
    `_fetch_archive_bytes`), so there is no re-fetching from any legislature's site regardless
    of which of those two sources actually has the bytes.

    Idempotent: a second run finds nothing stale and rewrites nothing.

    Dry run reports how many documents are stale. It deliberately does NOT predict the diff
    recompute, because `recompute_bill_diff_order` reads `raw_text` from the database -- with
    nothing committed it would be recomputing against the stale text, and reporting that number
    would be worse than reporting none.
    """
    init_django()
    from openstates.data.models import Bill

    if state == "all":
        bills = Bill.objects.all()
    elif session:
        bills = Bill.objects.filter(
            legislative_session__jurisdiction_id=abbr_to_jid(state),
            legislative_session__identifier=session,
        )
    else:
        bills = Bill.objects.filter(
            legislative_session__jurisdiction_id=abbr_to_jid(state)
        )
    bills = bills.filter(version_documents__isnull=False).distinct()
    if n:
        bills = bills[: int(n)]

    bills_touched = 0
    docs_stale = 0
    docs_skipped = 0
    docs_refused = 0
    diffs_corrected = 0
    diffs_would_change = 0
    skip_reasons: dict[str, int] = {}

    class _Proposed:
        """Stand-in carrying a document's PROPOSED text, for simulating the diff recompute in a
        dry run without writing anything. `recomputed_diffs_for_documents` reads only these
        attributes, which is why it was split out from its database-querying caller."""

        __slots__ = (
            "version_note", "version_date", "media_type",
            "raw_text", "is_error", "diff_from_previous_version",
        )

        def __init__(self, doc, raw_text, is_error):
            self.version_note = doc.version_note
            self.version_date = doc.version_date
            self.media_type = doc.media_type
            self.raw_text = raw_text
            self.is_error = is_error
            self.diff_from_previous_version = doc.diff_from_previous_version

    for bill in bills:
        proposed = []
        stale_docs = []
        for doc in bill.version_documents.all():
            result = _reextract_document(doc)
            if not result["attempted"]:
                docs_skipped += 1
                reason = result["reason"]
                skip_reasons[reason] = skip_reasons.get(reason, 0) + 1
                continue

            # Strict, not `.get(..., "")`. _reextract_document has an attempted=True branch that
            # returns NEITHER key (the DoNotDownload media types) and another that returns
            # new_is_error=True (an extractor exception). Defaulting those to empty text and
            # is_error=True would overwrite a perfectly good stored extraction with nothing --
            # real, reachable data loss on a ~51,900-document migration. Raised by /pm-review.
            if "new_raw_text" not in result or "new_is_error" not in result:
                docs_skipped += 1
                reason = result.get("reason", "helper returned no extraction")
                skip_reasons[reason] = skip_reasons.get(reason, 0) + 1
                continue
            new_raw_text = result["new_raw_text"]
            new_is_error = result["new_is_error"]

            # Never downgrade. This command exists to give documents BETTER text; a document
            # that currently extracts worse than what is stored is a signal to look at, not a
            # row to overwrite.
            currently_good = bool(doc.raw_text) and not doc.is_error
            now_worse = new_is_error or not new_raw_text
            if currently_good and now_worse:
                docs_refused += 1
                continue

            if new_raw_text == doc.raw_text and new_is_error == doc.is_error:
                proposed.append(_Proposed(doc, doc.raw_text, doc.is_error))
                continue
            docs_stale += 1
            stale_docs.append((doc, new_raw_text, new_is_error))
            proposed.append(_Proposed(doc, new_raw_text, new_is_error))

        if not stale_docs:
            continue
        bills_touched += 1

        if not commit:
            # Simulate the recompute against the PROPOSED text, so a dry run reports the thing
            # this migration is actually for rather than only how many documents would change.
            diffs_would_change += len(
                recomputed_diffs_for_documents(
                    proposed,
                    jurisdiction_name=bill.legislative_session.jurisdiction.name,
                    is_bill=bill.classification == ["bill"],
                )["changed"]
            )
            continue

        # One transaction per bill. The ordering below -- every version brought current before
        # any diff is recomputed -- is only an invariant if it cannot be interrupted halfway,
        # which would leave refreshed text paired with diffs computed from the old text.
        with transaction.atomic():
            for doc, new_raw_text, new_is_error in stale_docs:
                doc.raw_text = new_raw_text
                doc.is_error = new_is_error
                doc.save(update_fields=["raw_text", "is_error", "updated_at"])

            for doc, new_diff in recompute_bill_diff_order(bill)["changed"]:
                doc.diff_from_previous_version = new_diff
                doc.save(update_fields=["diff_from_previous_version", "updated_at"])
                diffs_corrected += 1

    mode = "COMMITTED" if commit else "DRY RUN"
    click.secho(
        f"{state}: [{mode}] bills_with_stale_docs={bills_touched} "
        f"stale_docs={docs_stale} "
        f"{'diffs_corrected' if commit else 'diffs_would_change'}="
        f"{diffs_corrected if commit else diffs_would_change} "
        f"docs_skipped={docs_skipped} docs_refused={docs_refused}",
        fg="green" if commit else "yellow",
    )
    if docs_refused:
        click.secho(
            f"  refused {docs_refused} document(s): stored text is good but the current "
            "extractor returns empty/errored output -- not overwritten, worth investigating",
            fg="red",
        )
    if skip_reasons:
        for reason, count in sorted(skip_reasons.items(), key=lambda kv: -kv[1])[:10]:
            click.secho(f"  skipped {count}: {reason}", fg="yellow")
