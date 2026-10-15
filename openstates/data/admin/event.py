from django.contrib import admin
from django.template import defaultfilters
from . import base
from .. import models


@admin.register(models.EventLocation)
class EventLocationAdmin(admin.ModelAdmin):
    pass


class EventParticipantInline(base.RelatedEntityInline):
    model = models.EventParticipant
    readonly_fields = ("organization", "person")


@admin.register(models.Event)
class EventAdmin(admin.ModelAdmin):
    readonly_fields = ("jurisdiction", "location")
    fields = (
        "name",
        "jurisdiction",
        "location",
        "description",
        "classification",
        "status",
        ("start_date", "end_date", "all_day"),
    )

    @admin.display(description="View source")
    def source_link(self, obj):
        source = obj.sources.filter(url__icontains="meetingdetail").get()
        tmpl = '<a href="{0}" target="_blank">View source</a>'
        return tmpl.format(source.url)

    list_display = ("jurisdiction", "name", "start_date", "source_link")

    inlines = [EventParticipantInline]


@admin.register(models.EventMedia)
class EventMediaAdmin(admin.ModelAdmin):
    pass


@admin.register(models.EventDocument)
class EventDocumentAdmin(admin.ModelAdmin):
    readonly_fields = ("event",)
    list_display = ("event", "date", "note")


@admin.register(models.EventSource)
class EventSourceAdmin(admin.ModelAdmin):
    readonly_fields = ("event",)


@admin.register(models.EventParticipant)
class EventParticipantAdmin(admin.ModelAdmin):
    pass


@admin.register(models.EventAgendaItem)
class EventAgendaItemAdmin(admin.ModelAdmin):
    readonly_fields = ("event",)
    fields = ("event", "description", "classification", "order", "subjects", "notes")

    @admin.display(description="Description")
    def get_truncated_description(self, obj):
        return defaultfilters.truncatewords(obj.description, 25)

    @admin.display(description="Event Name")
    def get_truncated_event_name(self, obj):
        return defaultfilters.truncatewords(obj.event.name, 8)

    list_display = ("get_truncated_event_name", "get_truncated_description")


@admin.register(models.EventRelatedEntity)
class EventRelatedEntityAdmin(admin.ModelAdmin):
    pass


@admin.register(models.EventAgendaMedia)
class EventAgendaMediaAdmin(admin.ModelAdmin):
    pass
