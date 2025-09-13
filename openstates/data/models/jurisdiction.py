import datetime
from django.db import models
from zoneinfo import ZoneInfo
from ..common import JURISDICTION_CLASSIFICATION_CHOICES, SESSION_CLASSIFICATION_CHOICES
from .base import OCDBase, OCDIDField, RelatedBase
from .division import Division


class Jurisdiction(OCDBase):
    """
    A Jurisdiction represents a logical unit of governance.

    Examples would include: the United States Federal Government, the Government
    of the District of Columbia, the Lexington-Fayette Urban County Government,
    or the Wake County Public School System.
    """

    id = OCDIDField(ocd_type="jurisdiction")
    name = models.CharField(
        max_length=300,
        help_text="The common name of the Jurisdiction, such as 'Wyoming.'",
    )
    url = models.URLField(
        max_length=2000, help_text="The primary website of the Jurisdiction."
    )
    classification = models.CharField(
        max_length=50,
        choices=JURISDICTION_CLASSIFICATION_CHOICES,
        default="state",
        db_index=True,
        help_text="The type of Jurisdiction being defined.",
    )
    division = models.ForeignKey(
        Division,
        related_name="jurisdictions",
        db_index=True,
        null=True,
        help_text="A link to a Division related to this Jurisdiction.",
        # don't allow deletion of a division that a Jurisdiction depends upon
        on_delete=models.PROTECT,
    )
    latest_bill_update = models.DateTimeField(
        default=datetime.datetime(2021, 1, 1, tzinfo=ZoneInfo("UTC"))
    )
    latest_people_update = models.DateTimeField(
        default=datetime.datetime(2021, 1, 1, tzinfo=ZoneInfo("UTC"))
    )

    class Meta:
        db_table = "opencivicdata_jurisdiction"

    def __str__(self):
        return self.name


class LegislativeSession(RelatedBase):
    jurisdiction = models.ForeignKey(
        Jurisdiction,
        related_name="legislative_sessions",
        # should be hard to delete Jurisdiction
        on_delete=models.PROTECT,
    )
    identifier = models.CharField(max_length=100)
    name = models.CharField(max_length=300)
    classification = models.CharField(
        max_length=100, choices=SESSION_CLASSIFICATION_CHOICES, blank=True
    )
    start_date = models.CharField(max_length=10)  # YYYY[-MM[-DD]]
    end_date = models.CharField(max_length=10)  # YYYY[-MM[-DD]]
    active = models.BooleanField(default=False)

    def __str__(self):
        return "{} {}".format(self.jurisdiction, self.name)

    class Meta:
        db_table = "opencivicdata_legislativesession"
