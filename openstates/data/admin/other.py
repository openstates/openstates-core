from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from openstates.data.admin.organization import OrganizationInline

from .. import models
from .base import ModelAdmin, ReadOnlyTabularInline


class JurisdictionInline(ReadOnlyTabularInline):
    model = models.Jurisdiction
    list_display = ("name", "id")
    readonly_fields = fields = (
        "get_id",
        "name",
        "classification",
        "extras",
        "url",
    )
    ordering = ("id",)

    def get_id(self, jurisdiction):
        admin_url = reverse(
            "admin:data_jurisdiction_change", args=(jurisdiction.pk,)
        )
        tmpl = u'<a href="%s">%s</a>'
        return format_html(tmpl % (admin_url, jurisdiction.name))

    get_id.short_description = "ID"
    get_id.allow_tags = True
    get_id.admin_order_field = "jurisdiction__name"


@admin.register(models.Division)
class DivisionAdmin(ModelAdmin):
    list_display = ("name", "id")
    search_fields = list_display
    fields = readonly_fields = ("id", "name", "redirect", "country")
    ordering = ("id",)
    inlines = [JurisdictionInline]


class LegislativeSessionInline(ReadOnlyTabularInline):
    model = models.LegislativeSession
    readonly_fields = ("identifier", "get_name", "classification", "start_date", "end_date")
    fields = readonly_fields
    ordering = ("-identifier",)

    def get_name(self, legislative_session):
        admin_url = reverse(
            "admin:data_legislativesession_change", args=(legislative_session.pk,)
        )
        tmpl = u'<a href="%s">%s</a>'
        return format_html(tmpl % (admin_url, legislative_session.name))

    get_name.short_description = "NAME"
    get_name.allow_tags = True


class BillInline(ReadOnlyTabularInline):
    model = models.Bill
    readonly_fields = fields = (
        "get_identifier",
        "classification",
        "from_organization",
        "title",
        "latest_action_date",
        "subject",
    )
    ordering = ("identifier",)

    def get_identifier(self, bill):
        admin_url = reverse(
            "admin:data_bill_change", args=(bill.id,)
        )
        tmpl = u'<a href="%s">%s</a>'
        return format_html(tmpl % (admin_url, bill.identifier))


@admin.register(models.LegislativeSession)
class LegislativeSessionAdmin(ModelAdmin):
    readonly_fields = ("jurisdiction", "identifier", "name", "active", "classification", "start_date", "end_date")
    inlines = [BillInline]


@admin.register(models.Jurisdiction)
class JurisdictionAdmin(ModelAdmin):
    list_display = ("name", "id", "classification")
    readonly_fields = fields = (
        "id",
        "name",
        "division",
        "classification",
        "extras",
        "url",
    )
    ordering = ("-classification", "id",)
    search_fields = ("id", "name")
    inlines = [LegislativeSessionInline, OrganizationInline]
