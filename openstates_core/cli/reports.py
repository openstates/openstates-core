import logging
from django.db import transaction
from django.db.models import Count, Subquery, OuterRef, Q, F
from .. import utils

# model imports are inside functions since this file is imported pre-init

logger = logging.getLogger("openstates")


def print_report(report):
    plan = report["plan"]
    print("{} ({})".format(plan["module"], ", ".join(plan["actions"])))
    for scraper, args in plan["scrapers"].items():
        print("  {}: {}".format(scraper, args))
    if "scrape" in report:
        for type, details in sorted(report["scrape"].items()):
            print(type + " scrape:")
            print("  duration: ", (details["end"] - details["start"]))
            print("  objects:")
            for objtype, num in sorted(details["objects"].items()):
                print("    {}: {}".format(objtype, num))
    if "import" in report:
        print("import:")
        for type, changes in sorted(report["import"].items()):
            if changes["insert"] or changes["update"] or changes["noop"]:
                print(
                    "  {}: {} new {} updated {} noop".format(
                        type, changes["insert"], changes["update"], changes["noop"]
                    )
                )


@transaction.atomic
def save_report(report, jurisdiction):
    from ..reports.models import RunPlan
    from ..data.models import Jurisdiction

    # set end time
    report["end"] = utils.utcnow()

    # if there's an error on the first run, the jurisdiction doesn't exist
    # yet, we opt for skipping creation of RunPlan until there's been at least
    # one good run
    try:
        Jurisdiction.objects.get(pk=jurisdiction)
    except Jurisdiction.DoesNotExist:
        logger.warning(
            "could not save RunPlan, no successful runs of {} yet".format(jurisdiction)
        )
        return

    plan = RunPlan.objects.create(
        jurisdiction_id=jurisdiction,
        success=report["success"],
        start_time=report["start"],
        end_time=report["end"],
        exception=report.get("exception", ""),
        traceback=report.get("traceback", ""),
    )

    for scraper, details in report.get("scrape", {}).items():
        args = " ".join(
            "{k}={v}".format(k=k, v=v)
            for k, v in report["plan"]["scrapers"].get(scraper, {}).items()
        )
        sr = plan.scrapers.create(
            scraper=scraper,
            args=args,
            start_time=details["start"],
            end_time=details["end"],
        )
        for object_type, num in details["objects"].items():
            sr.scraped_objects.create(object_type=object_type, count=num)

    for object_type, changes in report.get("import", {}).items():
        if changes["insert"] or changes["update"] or changes["noop"]:
            plan.imported_objects.create(
                object_type=object_type,
                insert_count=changes["insert"],
                update_count=changes["update"],
                noop_count=changes["noop"],
                start_time=changes["start"],
                end_time=changes["end"],
            )


def _simple_count(ModelCls, session, **filter):
    return (
        ModelCls.objects.filter(legislative_session_id=session).filter(**filter).count()
    )


def generate_session_report(session):
    from ..data.models import Bill, VoteEvent, VoteCount, PersonVote, BillSponsorship
    from ..reports.models import SessionDataQualityReport

    report = {
        "bills_missing_actions": _simple_count(Bill, session, actions__isnull=True),
        "bills_missing_sponsors": _simple_count(
            Bill, session, sponsorships__isnull=True
        ),
        "bills_missing_versions": _simple_count(Bill, session, versions__isnull=True),
        "votes_missing_bill": _simple_count(VoteEvent, session, bill__isnull=True),
        "votes_missing_voters": _simple_count(VoteEvent, session, votes__isnull=True),
        "votes_missing_yes_count": 0,
        "votes_missing_no_count": 0,
        "votes_with_bad_counts": 0,
    }

    voteevents = VoteEvent.objects.filter(legislative_session_id=session)
    queryset = voteevents.annotate(
        yes_sum=Count("pk", filter=Q(votes__option="yes")),
        no_sum=Count("pk", filter=Q(votes__option="no")),
        other_sum=Count("pk", filter=Q(votes__option="other")),
        yes_count=Subquery(
            VoteCount.objects.filter(vote_event=OuterRef("pk"), option="yes").values(
                "value"
            )
        ),
        no_count=Subquery(
            VoteCount.objects.filter(vote_event=OuterRef("pk"), option="no").values(
                "value"
            )
        ),
        other_count=Subquery(
            VoteCount.objects.filter(vote_event=OuterRef("pk"), option="other").values(
                "value"
            )
        ),
    )

    for vote in queryset:
        if vote.yes_count is None:
            report["votes_missing_yes_count"] += 1
            vote.yes_count = 0
        if vote.no_count is None:
            report["votes_missing_no_count"] += 1
            vote.no_count = 0
        if vote.other_count is None:
            vote.other_count = 0
        if (
            vote.yes_sum != vote.yes_count
            or vote.no_sum != vote.no_count
            or vote.other_sum != vote.other_count
        ):
            report["votes_with_bad_counts"] += 1

    # handle unmatched
    queryset = (
        BillSponsorship.objects.filter(
            bill__legislative_session_id=session, entity_type="person", person_id=None
        )
        .values("name")
        .annotate(num=Count("name"))
    )
    report["unmatched_sponsor_people"] = {
        item["name"]: item["num"] for item in queryset
    }
    queryset = (
        BillSponsorship.objects.filter(
            bill__legislative_session_id=session,
            entity_type="organization",
            person_id=None,
        )
        .values("name")
        .annotate(num=Count("name"))
    )
    report["unmatched_sponsor_organizations"] = {
        item["name"]: item["num"] for item in queryset
    }
    queryset = (
        PersonVote.objects.filter(
            vote_event__legislative_session_id=session, voter__isnull=True
        )
        .values(name=F("voter_name"))
        .annotate(num=Count("voter_name"))
    )
    report["unmatched_voters"] = {item["name"]: item["num"] for item in queryset}

    # atomically replace the report if it exists
    new_report = SessionDataQualityReport(legislative_session_id=session, **report)
    with transaction.atomic():
        SessionDataQualityReport.objects.filter(legislative_session=session).delete()
        new_report.save()

    return new_report
