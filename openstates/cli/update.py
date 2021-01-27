from collections import OrderedDict
import argparse
import contextlib
import glob
import importlib
import logging
import logging.config
import os
import sys
import traceback

from django.db import transaction

from ..exceptions import CommandError
from ..scrape import Jurisdiction, JurisdictionScraper
from ..utils.django import init_django
from .. import utils, settings
from .reports import generate_session_report, print_report, save_report

logger = logging.getLogger("openstates")


ALL_ACTIONS = ("scrape", "import")


class _Unset:
    pass


UNSET = _Unset()


@contextlib.contextmanager
def override_settings(settings, overrides):
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


def get_jurisdiction(module_name):
    # get the jurisdiction object
    module = importlib.import_module(module_name)
    for obj in module.__dict__.values():
        # ensure we're dealing with a subclass of Jurisdiction
        if (
            isinstance(obj, type)
            and issubclass(obj, Jurisdiction)
            and getattr(obj, "division_id", None)
            and obj.classification
        ):
            return obj(), module
    raise CommandError(
        "Unable to import Jurisdiction subclass from "
        + module_name
        + ". Jurisdiction subclass may be missing a "
        + "division_id or classification."
    )


def do_scrape(juris, args, scrapers):
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
        juris, datadir, strict_validation=args.strict, fastmode=args.fastmode
    )
    report["jurisdiction"] = jscraper.do_scrape()

    for scraper_name, scrape_args in scrapers.items():
        ScraperCls = juris.scrapers[scraper_name]
        scraper = ScraperCls(
            juris, datadir, strict_validation=args.strict, fastmode=args.fastmode
        )
        report[scraper_name] = scraper.do_scrape(**scrape_args)

    return report


def do_import(juris, args):
    # import inside here because to avoid loading Django code unnecessarily
    from openstates.importers import (
        JurisdictionImporter,
        BillImporter,
        VoteEventImporter,
    )

    datadir = os.path.join(settings.SCRAPED_DATA_DIR, args.module)

    juris_importer = JurisdictionImporter(juris.jurisdiction_id)
    bill_importer = BillImporter(juris.jurisdiction_id)
    vote_event_importer = VoteEventImporter(juris.jurisdiction_id, bill_importer)
    report = {}

    with transaction.atomic():
        print("import jurisdictions...")
        report.update(juris_importer.import_directory(datadir))
        if settings.ENABLE_BILLS:
            print("import bills...")
            report.update(bill_importer.import_directory(datadir))
        if settings.ENABLE_VOTES:
            print("import vote events...")
            report.update(vote_event_importer.import_directory(datadir))

    # compile info on all sessions that were updated in this run
    seen_sessions = set()
    seen_sessions.update(bill_importer.get_seen_sessions())
    seen_sessions.update(vote_event_importer.get_seen_sessions())
    for session in seen_sessions:
        generate_session_report(session)

    return report


def check_session_list(juris):
    scraper = type(juris).__name__

    # if get_session_list is not defined
    if not hasattr(juris, "get_session_list"):
        raise CommandError(f"{scraper}.get_session_list() is not provided")

    scraped_sessions = juris.get_session_list()

    if not scraped_sessions:
        raise CommandError("no sessions from {}.get_session_list()".format(scraper))

    # copy the list to avoid modifying it
    sessions = set(juris.ignored_scraped_sessions)
    for session in juris.legislative_sessions:
        sessions.add(session.get("_scraped_name", session["identifier"]))

    unaccounted_sessions = list(set(scraped_sessions) - sessions)
    if unaccounted_sessions:
        raise CommandError(
            (
                "Session(s) {sessions} were reported by {scraper}.get_session_list() "
                "but were not found in {scraper}.legislative_sessions or "
                "{scraper}.ignored_scraped_sessions."
            ).format(sessions=", ".join(unaccounted_sessions), scraper=scraper)
        )


def do_update(args, other, juris):
    available_scrapers = getattr(juris, "scrapers", {})
    default_scrapers = getattr(juris, "default_scrapers", None)
    scrapers = OrderedDict()

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
        check_session_list(juris)

    try:
        if "scrape" in args.actions:
            report["scrape"] = do_scrape(juris, args, scrapers)
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


def parse_args():
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

    # process args
    return parser.parse_known_args()


def main():
    args, other = parse_args()

    # set log level from command line
    handler_level = getattr(logging, args.loglevel.upper(), "INFO")
    settings.LOGGING["handlers"]["default"]["level"] = handler_level
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
        def _tb_info(type, value, tb):
            traceback.print_exception(type, value, tb)
            debug_module.pm()

        sys.excepthook = _tb_info

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
    main()
