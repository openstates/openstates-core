from django.db import models  # type: ignore
from .jurisdiction import Jurisdiction, LegislativeSession


OBJECT_TYPES = (
    ("jurisdiction", "Jurisdiction"),
    ("person", "Person"),
    ("organization", "Organization"),
    ("post", "Post"),
    ("membership", "Membership"),
    ("bill", "Bill"),
    ("vote_event", "VoteEvent"),
    ("event", "Event"),
)


class RunPlan(models.Model):
    jurisdiction = models.ForeignKey(
        Jurisdiction, related_name="runs", on_delete=models.CASCADE
    )
    success = models.BooleanField(default=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    exception = models.TextField(blank=True, default="")
    traceback = models.TextField(blank=True, default="")

    class Meta:
        db_table = "pupa_runplan"


class ScrapeReport(models.Model):
    plan = models.ForeignKey(RunPlan, related_name="scrapers", on_delete=models.CASCADE)
    scraper = models.CharField(max_length=300)
    args = models.CharField(max_length=300)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    class Meta:
        db_table = "pupa_scrapereport"


class ScrapeObjects(models.Model):
    report = models.ForeignKey(
        ScrapeReport, related_name="scraped_objects", on_delete=models.CASCADE
    )
    object_type = models.CharField(max_length=20, choices=OBJECT_TYPES)
    count = models.PositiveIntegerField()

    class Meta:
        db_table = "pupa_scrapeobjects"


class ImportObjects(models.Model):
    report = models.ForeignKey(
        RunPlan, related_name="imported_objects", on_delete=models.CASCADE
    )
    object_type = models.CharField(max_length=20, choices=OBJECT_TYPES)
    insert_count = models.PositiveIntegerField()
    update_count = models.PositiveIntegerField()
    noop_count = models.PositiveIntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    records = models.JSONField(blank=True, null=True)

    class Meta:
        db_table = "pupa_importobjects"


class SessionDataQualityReport(models.Model):
    legislative_session = models.ForeignKey(
        LegislativeSession, on_delete=models.CASCADE
    )

    bills_missing_actions = models.PositiveIntegerField()
    bills_missing_sponsors = models.PositiveIntegerField()
    bills_missing_versions = models.PositiveIntegerField()

    votes_missing_voters = models.PositiveIntegerField()
    votes_missing_bill = models.PositiveIntegerField()
    votes_missing_yes_count = models.PositiveIntegerField()
    votes_missing_no_count = models.PositiveIntegerField()
    votes_with_bad_counts = models.PositiveIntegerField()

    # these fields store lists of names mapped to numbers of occurances
    unmatched_sponsor_people = models.JSONField()
    unmatched_sponsor_organizations = models.JSONField()
    unmatched_voters = models.JSONField()

    class Meta:
        db_table = "pupa_sessiondataqualityreport"
