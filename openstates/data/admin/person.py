from django.urls import reverse
from django.contrib import admin
from django.utils.safestring import mark_safe
from .. import models
from .base import (
    ModelAdmin,
    ReadOnlyTabularInline,
    IdentifierInline,
    OtherNameInline,
)


class PersonIdentifierInline(IdentifierInline):
    model = models.PersonIdentifier


class PersonNameInline(OtherNameInline):
    model = models.PersonName


class PersonOfficeInline(ReadOnlyTabularInline):
    readonly_fields = ("classification", "address", "voice", "fax", "name")
    model = models.PersonOffice


class PersonLinkInline(ReadOnlyTabularInline):
    readonly_fields = ("url", "note")
    model = models.PersonLink


class PersonSourceInline(ReadOnlyTabularInline):
    readonly_fields = ("url", "note")
    model = models.PersonSource


class MembershipInline(ReadOnlyTabularInline):
    model = models.Membership
    readonly_fields = ("organization", "person", "post", "role", "start_date")
    fields = ("id",) + readonly_fields + ("end_date",)
    exclude = ("id",)
    extra = 0
    can_delete = False
    ordering = ("end_date",)


# TODO field locking
@admin.register(models.Person)
class PersonAdmin(ModelAdmin):
    search_fields = ["name"]
    readonly_fields = ("id", "name", "extras")
    fields = (
        "name",
        "id",
        "image",
        ("birth_date", "death_date"),
        "gender",
        "biography",
        "extras",
    )
    ordering = ("name",)
    list_filter = ("memberships__organization__jurisdiction__name",)

    inlines = [
        PersonIdentifierInline,
        PersonNameInline,
        PersonOfficeInline,
        PersonLinkInline,
        PersonSourceInline,
        MembershipInline,
    ]

    @admin.display(description="Memberships")
    def get_memberships(self, obj):
        memberships = obj.memberships.select_related("organization__jurisdiction")
        html = []
        SHOW_N = 5
        for memb in memberships[:SHOW_N]:
            org = memb.organization
            admin_url = reverse("admin:data_organization_change", args=(org.pk,))
            tmpl = '<a href="%s">%s%s</a>\n'
            html.append(
                tmpl
                % (
                    admin_url,
                    (
                        memb.organization.jurisdiction.name + ": "
                        if memb.organization.jurisdiction
                        else ""
                    ),
                    memb.organization.name,
                )
            )
        more = len(memberships) - SHOW_N
        if 0 < more:
            html.append("And %d more" % more)
        return mark_safe("<br/>".join(html))

    list_display = ("name", "id", "get_memberships")
