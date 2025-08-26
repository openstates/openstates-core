from django.contrib import admin
from django.template import defaultfilters
from .base import ModelAdmin, ReadOnlyTabularInline, IdentifierInline
from .. import models
from django.utils.html import format_html_join


class BillAbstractInline(ReadOnlyTabularInline):
    model = models.BillAbstract
    readonly_fields = ("abstract", "note")
    can_delete = False


class BillTitleInline(ReadOnlyTabularInline):
    model = models.BillTitle
    readonly_fields = ("title", "note")
    can_delete = False


class BillIdentifierInline(IdentifierInline):
    model = models.BillIdentifier
    fields = readonly_fields = ["identifier"]


class BillActionInline(ReadOnlyTabularInline):
    model = models.BillAction

    @admin.display(description="Related Entities")
    def get_related_entities(self, obj):
        ents = obj.related_entities.all()
        ent_list = [e.name for e in ents]
        return ", ".join(ent_list)

    list_select_related = ("BillActionRelatedEntity",)
    readonly_fields = fields = (
        "date",
        "organization",
        "description",
        "get_related_entities",
    )


class RelatedBillInline(ReadOnlyTabularInline):
    model = models.RelatedBill
    fk_name = "bill"
    readonly_fields = fields = ("identifier", "legislative_session", "relation_type")
    extra = 0


class BillSponsorshipInline(ReadOnlyTabularInline):
    model = models.BillSponsorship
    readonly_fields = fields = ("person", "primary", "classification")
    ordering = ("classification", "name")
    extra = 0


class DocVersionInline(ReadOnlyTabularInline):
    model = models.BillVersion

    @admin.display(description="Links")
    def get_links(self, obj):
        return format_html_join(
            "<br />",
            '<a href="{}" target="_blank">{}</a>',
            ((link.url, link.url) for link in obj.links.all()),
        )

    list_select_related = ("BillVersionLink",)
    readonly_fields = ("note", "date", "get_links")


class BillVersionInline(DocVersionInline):
    model = models.BillVersion
    readonly_fields = fields = ("date", "note", "classification")


class BillDocumentInline(DocVersionInline):
    model = models.BillDocument


class BillSourceInline(ReadOnlyTabularInline):
    readonly_fields = ("url", "note")
    model = models.BillSource


@admin.register(models.Bill)
class BillAdmin(ModelAdmin):
    readonly_fields = fields = (
        "identifier",
        "legislative_session",
        "bill_classifications",
        "from_organization",
        "title",
        "id",
        "subject",
        "extras",
    )
    search_fields = ["identifier", "title", "legislative_session__jurisdiction__name"]
    list_select_related = ("legislative_session", "legislative_session__jurisdiction")
    inlines = [
        BillAbstractInline,
        BillTitleInline,
        BillIdentifierInline,
        BillActionInline,
        BillSponsorshipInline,
        BillSourceInline,
        RelatedBillInline,
        BillVersionInline,
        BillDocumentInline,
    ]

    def bill_classifications(self, obj):
        return ", ".join(obj.classification)

    @admin.display(description="Jurisdiction")
    def get_jurisdiction_name(self, obj):
        return obj.legislative_session.jurisdiction.name

    @admin.display(
        description="Session",
        ordering="legislative_session__name",
    )
    def get_session_name(self, obj):
        return obj.legislative_session.name

    @admin.display(description="Sponsors")
    def get_truncated_sponsors(self, obj):
        spons = ", ".join(s.name for s in obj.sponsorships.all()[:5])
        return defaultfilters.truncatewords(spons, 10)

    @admin.display(description="Title")
    def get_truncated_title(self, obj):
        return defaultfilters.truncatewords(obj.title, 25)

    list_display = (
        "identifier",
        "get_jurisdiction_name",
        "get_session_name",
        "get_truncated_sponsors",
        "get_truncated_title",
    )

    list_filter = ("legislative_session__jurisdiction__name",)
    ordering = (
        "legislative_session__jurisdiction__name",
        "legislative_session",
        "identifier",
    )
