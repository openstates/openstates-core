from django.contrib import admin
from .. import models
from .base import ModelAdmin, ReadOnlyTabularInline


@admin.register(models.Division)
class DivisionAdmin(ModelAdmin):
    list_display = ("name", "id")
    search_fields = list_display
    fields = readonly_fields = ("id", "name", "redirect", "country")
    ordering = ("id",)


class LegislativeSessionInline(ReadOnlyTabularInline):
    model = models.LegislativeSession
    readonly_fields = ("identifier", "name", "classification", "start_date", "end_date")
    ordering = ("-identifier",)


@admin.register(models.Jurisdiction)
class JurisdictionAdmin(ModelAdmin):
    list_display = ("name", "id")
    readonly_fields = fields = (
        "id",
        "name",
        "division",
        "classification",
        "extras",
        "url",
    )
    ordering = ("id",)
    inlines = [LegislativeSessionInline]
