from django.contrib import admin
from .base import ModelAdmin, ReadOnlyTabularInline
from .. import models


class VoteCountInline(ReadOnlyTabularInline):
    model = models.VoteCount
    fields = readonly_fields = ("option", "value")


class PersonVoteInline(ReadOnlyTabularInline):
    model = models.PersonVote
    fields = readonly_fields = ("voter", "voter_name", "option")


class VoteSourceInline(ReadOnlyTabularInline):
    model = models.VoteSource
    fields = readonly_fields = ("url", "note")


@admin.register(models.VoteEvent)
class VoteEventAdmin(ModelAdmin):
    readonly_fields = (
        "bill",
        "organization",
        "legislative_session",
        "id",
        "identifier",
        "motion_text",
        "extras",
    )
    fields = readonly_fields + (
        "result",
        "motion_classification",
        "start_date",
    )

    list_selected_related = (
        "sources",
        "legislative_session",
        "legislative_session__jurisdiction",
        "counts",
    )

    @admin.display(description="Jurisdiction")
    def get_jurisdiction_name(self, obj):
        return obj.legislative_session.jurisdiction.name

    @admin.display(description="Vote Tally")
    def get_vote_tally(self, obj):
        yes = no = other = 0
        for vc in obj.counts.all():
            if vc.option == "yes":
                yes = vc.value
            elif vc.option == "no":
                no = vc.value
            else:
                other += vc.value
        return "{}-{}-{}".format(yes, no, other)

    list_display = ("get_jurisdiction_name", "identifier", "bill", "get_vote_tally")

    list_filter = ("legislative_session__jurisdiction__name",)

    inlines = [VoteCountInline, PersonVoteInline, VoteSourceInline]
