import argparse
import contextlib
import datetime
import glob
import importlib
import inspect
import logging
import logging.config
import os
import sys
import traceback
import typing
from collections import defaultdict
from types import ModuleType

import boto3  # type: ignore
from django.db import transaction  # type: ignore

from .. import settings, utils
from ..exceptions import CommandError
from ..scrape import JurisdictionScraper, State
from ..utils.django import init_django
from .reports import generate_session_report, print_report, save_report

logger = logging.getLogger("openstates")


ALL_ACTIONS = ("scrape", "import")


class _Unset:
    pass


UNSET = _Unset()


@contextlib.contextmanager
def override_settings(settings, overrides):  # type: ignore
    original = {}
    for key, value in overrides.items():
        original[key] = getattr(settings, key, UNSET)
        setattr(settings, key, value)
    yield
    for key, value in original.items():
        if value is UNSET:
            delattr(settings, key)
        else:
            setattr(settings, key, value)


def get_jurisdiction(module_name: str) -> tuple[State, ModuleType]:
    # get the state object
    module = importlib.import_module(module_name)
    for obj in module.__dict__.values():
        # ensure we're dealing with a subclass of State
        if isinstance(obj, type) and issubclass(obj, State) and obj != State:
            return obj(), module
    raise CommandError(f"Unable to import State subclass from {module_name}")


def do_scrape(
    juris: State,
    args: argparse.Namespace,
    scrapers: dict[str, dict[str, str]],
    active_sessions: set[str],
) -> dict[str, typing.Any]:
    # make output and cache dirs
    utils.makedirs(settings.CACHE_DIR)
    datadir = os.path.join(settings.SCRAPED_DATA_DIR, args.module)
    utils.makedirs(datadir)
    # clear json from data dir
    for f in glob.glob(datadir + "/*.json"):
        os.remove(f)

    report = {}

    # do jurisdiction
    jscraper = JurisdictionScraper(
        juris,
        datadir,
        strict_validation=args.strict,
        fastmode=args.fastmode,
        realtime=args.realtime,
    )
    report["jurisdiction"] = jscraper.do_scrape()

    for scraper_name, scrape_args in scrapers.items():
        ScraperCls = juris.scrapers[scraper_name]
        if (
            "session" in inspect.getargspec(ScraperCls.scrape).args
            and "session" not in scrape_args
        ):
            print(f"no session provided, using active sessions: {active_sessions}")
            # handle automatically setting session if required by the scraper
            # the report logic was originally meant for one run, so we combine the start & end times
            # and counts here
            report[scraper_name] = {
                "start": None,
                "end": None,
                "objects": defaultdict(int),
            }
            for session in active_sessions:
                # new scraper each time
                scraper = ScraperCls(
                    juris,
                    datadir,
                    strict_validation=args.strict,
                    fastmode=args.fastmode,
                    realtime=args.realtime,
                )
                partial_report = scraper.do_scrape(**scrape_args, session=session)
                if not report[scraper_name]["start"]:
                    report[scraper_name]["start"] = partial_report["start"]
                report[scraper_name]["end"] = partial_report["end"]
                for obj, val in partial_report["objects"].items():
                    report[scraper_name]["objects"][obj] += val
        else:
            scraper = ScraperCls(
                juris,
                datadir,
                strict_validation=args.strict,
                fastmode=args.fastmode,
                realtime=args.realtime,
            )
            report[scraper_name] = scraper.do_scrape(**scrape_args)

    return report


def do_import(juris: State, args: argparse.Namespace) -> dict[str, typing.Any]:
    # import inside here because to avoid loading Django code unnecessarily
    from openstates.data.models import Jurisdiction as DatabaseJurisdiction
    from openstates.importers import (
        BillImporter,
        EventImporter,
        JurisdictionImporter,
        VoteEventImporter,
    )

    datadir = os.path.join(settings.SCRAPED_DATA_DIR, args.module)

    juris_importer = JurisdictionImporter(juris.jurisdiction_id)
    bill_importer = BillImporter(juris.jurisdiction_id)
    vote_event_importer = VoteEventImporter(juris.jurisdiction_id, bill_importer)
    event_importer = EventImporter(juris.jurisdiction_id, vote_event_importer)
    report = {}

    with transaction.atomic():
        print("import jurisdictions...")
        report.update(juris_importer.import_directory(datadir))
        print("import bills...")
        report.update(bill_importer.import_directory(datadir))
        print("import vote events...")
        report.update(vote_event_importer.import_directory(datadir))
        print("import events...")
        report.update(event_importer.import_directory(datadir))
        DatabaseJurisdiction.objects.filter(id=juris.jurisdiction_id).update(
            latest_bill_update=datetime.datetime.utcnow()
        )

    # compile info on all sessions that were updated in this run
    seen_sessions = set()
    seen_sessions.update(bill_importer.get_seen_sessions())
    seen_sessions.update(vote_event_importer.get_seen_sessions())
    for session in seen_sessions:
        generate_session_report(session)

    return report


def check_session_list(juris: State) -> set[str]:
    scraper = type(juris).__name__

    # if get_session_list is not defined
    if not hasattr(juris, "get_session_list"):
        raise CommandError(f"{scraper}.get_session_list() is not provided")

    scraped_sessions = juris.get_session_list()

    if not scraped_sessions:
        raise CommandError("no sessions from {}.get_session_list()".format(scraper))

    active_sessions = set()
    # copy the list to avoid modifying it
    sessions = set(juris.ignored_scraped_sessions)
    for session in juris.legislative_sessions:
        sessions.add(session.get("_scraped_name", session["identifier"]))
        if session.get("active"):
            active_sessions.add(session.get("identifier"))

    if not active_sessions:
        raise CommandError(f"No active sessions on {scraper}")

    unaccounted_sessions = list(set(scraped_sessions) - sessions)
    if unaccounted_sessions:
        raise CommandError(
            (
                "Session(s) {sessions} were reported by {scraper}.get_session_list() "
                "but were not found in {scraper}.legislative_sessions or "
                "{scraper}.ignored_scraped_sessions."
            ).format(sessions=", ".join(unaccounted_sessions), scraper=scraper)
        )

    return active_sessions


def do_update(
    args: argparse.Namespace, other: list[str], juris: State
) -> dict[str, typing.Any]:
    available_scrapers = getattr(juris, "scrapers", {})
    default_scrapers = getattr(juris, "default_scrapers", None)
    scrapers: dict[str, dict[str, str]] = {}

    if not available_scrapers:
        raise CommandError("no scrapers defined on jurisdiction")

    if other:
        # parse arg list in format: (scraper (k:v)+)+
        cur_scraper = None
        for arg in other:
            if "=" in arg:
                if not cur_scraper:
                    raise CommandError("argument {} before scraper name".format(arg))
                k, v = arg.split("=", 1)
                scrapers[cur_scraper][k] = v
            elif arg in juris.scrapers:
                cur_scraper = arg
                scrapers[cur_scraper] = {}
            else:
                raise CommandError(
                    "no such scraper: module={} scraper={}".format(args.module, arg)
                )
    elif default_scrapers is not None:
        scrapers = {s: {} for s in default_scrapers}
    else:
        scrapers = {key: {} for key in available_scrapers.keys()}

    # modify args in-place so we can pass them around
    if not args.actions:
        args.actions = ALL_ACTIONS

    if "import" in args.actions:
        init_django()

    # print the plan
    report = {
        "plan": {"module": args.module, "actions": args.actions, "scrapers": scrapers},
        "start": utils.utcnow(),
    }
    print_report(report)

    if "scrape" in args.actions:
        active_sessions = check_session_list(juris)

    try:
        if "scrape" in args.actions:
            report["scrape"] = do_scrape(juris, args, scrapers, active_sessions)
        if "import" in args.actions:
            report["import"] = do_import(juris, args)
        report["success"] = True
    except Exception as exc:
        report["success"] = False
        report["exception"] = exc
        report["traceback"] = traceback.format_exc()
        if "import" in args.actions:
            save_report(report, juris.jurisdiction_id)
        raise

    if "import" in args.actions:
        save_report(report, juris.jurisdiction_id)

    print_report(report)
    return report


def parse_args() -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser("openstates", description="openstates CLI")
    parser.add_argument("--debug", action="store_true", help="open debugger on error")
    parser.add_argument(
        "--loglevel",
        default="INFO",
        help=(
            "set log level. options are: "
            "DEBUG|INFO|WARNING|ERROR|CRITICAL "
            "(default is INFO)"
        ),
    )
    # what to scrape
    parser.add_argument("module", type=str, help="path to scraper module")
    for arg in ALL_ACTIONS:
        parser.add_argument(
            "--" + arg,
            dest="actions",
            action="append_const",
            const=arg,
            help="only run {} post-scrape step".format(arg),
        )

    # scraper arguments
    parser.add_argument(
        "--nonstrict",
        action="store_false",
        dest="strict",
        help="skip validation on save",
    )
    parser.add_argument(
        "--fastmode", action="store_true", help="use cache and turn off throttling"
    )

    # settings overrides
    parser.add_argument("--datadir", help="data directory", dest="SCRAPED_DATA_DIR")
    parser.add_argument("--cachedir", help="cache directory", dest="CACHE_DIR")
    parser.add_argument(
        "-r", "--rpm", help="scraper rpm", type=int, dest="SCRAPELIB_RPM"
    )
    parser.add_argument(
        "--timeout", help="scraper timeout", type=int, dest="SCRAPELIB_TIMEOUT"
    )
    parser.add_argument(
        "--no-verify",
        help="skip tls verification",
        action="store_false",
        dest="SCRAPELIB_VERIFY",
    )
    parser.add_argument(
        "--retries", help="scraper retries", type=int, dest="SCRAPELIB_RETRIES"
    )
    parser.add_argument(
        "--retry_wait",
        help="scraper retry wait",
        type=int,
        dest="SCRAPELIB_RETRY_WAIT_SECONDS",
    )

    # realtime mode
    parser.add_argument("--realtime", action="store_true", help="enable realtime mode")

    # process args
    return parser.parse_known_args()


def delete_all_objects_from_s3_folder(module: str) -> None:
    """
    This function deletes all files in the current module's folder on S3. It is done to ensure that the files are not
    left over from a previous run for a jurisdiction. This is also not after runs because we want to keep the files
    for the previous run in case we need to revert, or check out issues during failures.

    Args:
        module (str): The module name for the jurisdiction that is being run.
    Example:
        delete_all_objects_from_s3_folder("il")
    """

    logging.info(f"Deleting initial objects from {module} folder")

    bucket_name = os.environ.get("S3_REALTIME_BASE")

    s3_client = boto3.client("s3")

    # First we list all files in folder
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=f"{module}/")
    if response.get("Contents") or response.get("KeyCount") == 0:

        files_in_folder = response["Contents"]

        # We will create a key array to pass to delete_objects function
        files_to_delete = [{"Key": f["Key"]} for f in files_in_folder]

        logging.info(f"Files to delete: {files_to_delete}")

        # This will delete all files in a folder
        s3_client.delete_objects(
            Bucket=bucket_name, Delete={"Objects": files_to_delete}
        )
    else:
        # files or folder (module) does not exist
        logging.info(f"No files found in {module} folder")


def main() -> int:
    args, other = parse_args()

    # set log level from command line
    handler_level = getattr(logging, args.loglevel.upper(), "INFO")
    settings.LOGGING["handlers"]["default"]["level"] = handler_level  # type: ignore
    logging.config.dictConfig(settings.LOGGING)

    # turn debug on
    if args.debug:
        try:
            debug_module = importlib.import_module("ipdb")
        except ImportError:
            debug_module = importlib.import_module("pdb")

        # turn on PDB-on-error mode
        # stolen from http://stackoverflow.com/questions/1237379/
        # if this causes problems in interactive mode check that page
        def _tb_info(type, value, tb):  # type: ignore
            traceback.print_exception(type, value, tb)
            debug_module.pm()

        sys.excepthook = _tb_info

    logging.info(f"Module: {args.module}")

    # delete all objects from S3 folder for current module
    delete_all_objects_from_s3_folder(args.module)

    juris, module = get_jurisdiction(args.module)

    overrides = {}
    overrides.update(getattr(module, "settings", {}))
    overrides.update(
        {key: value for key, value in vars(args).items() if value is not None}
    )
    with override_settings(settings, overrides):
        report = do_update(args, other, juris)

    if report.get("success", False):
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
