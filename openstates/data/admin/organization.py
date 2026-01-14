from django.urls import reverse
from django.contrib import admin
from django.utils.html import format_html

from openstates.data.admin.person import MembershipInline

from .. import models
from .base import ModelAdmin, ReadOnlyTabularInline


class PostInline(admin.TabularInline):
    """a read-only inline for posts here, with links to the real thing"""

    model = models.Post
    extra = 0
    fields = readonly_fields = ("get_label", "role")
    ordering = ("label",)
    can_delete = False

    @admin.display(description="Label")
    def get_label(self, post):
        admin_url = reverse("admin:data_post_change", args=(post.pk,))
        tmpl = '<a href="%s">%s</a>'
        return format_html(tmpl % (admin_url, post.label))

    def has_add_permission(self, request, obj=None):
        return False


class OrganizationInline(ReadOnlyTabularInline):
    """a read-only inline for posts here, with links to the real thing"""

    model = models.Organization
    fields = readonly_fields = ("get_name", "jurisdiction", "classification")
    ordering = ("-classification", "name")

    @admin.display(
        description="ID",
        ordering="organization__name",
    )
    def get_name(self, organization):
        admin_url = reverse("admin:data_organization_change", args=(organization.pk,))
        tmpl = '<a href="%s">%s</a>'
        return format_html(tmpl % (admin_url, organization.name))


class OrgMembershipInline(ReadOnlyTabularInline):
    model = models.Membership
    fk_name = "organization"
    readonly_fields = ("id", "person", "post", "role", "start_date")
    fields = readonly_fields + ("end_date",)
    extra = 0
    can_delete = False
    ordering = ("person__name", "start_date")


@admin.register(models.Post)
class PostAdmin(ModelAdmin):
    readonly_fields = fields = (
        "id",
        "division",
        "organization",
        "label",
        "role",
        "maximum_memberships",
        "extras",
    )
    ordering = ("division__id", "organization", "role", "label")
    inlines = (MembershipInline,)
    list_display = ("division", "organization", "role", "label")


@admin.register(models.Organization)
class OrganizationAdmin(ModelAdmin):
    readonly_fields = (
        "id",
        "name",
        "classification",
        "parent",
        "jurisdiction",
        "extras",
    )
    fields = readonly_fields
    search_fields = ("name",)
    list_filter = ("jurisdiction__name",)

    inlines = [
        PostInline,
        OrgMembershipInline,
        OrganizationInline,
    ]

    @admin.display(
        description="Name",
        ordering="name",
    )
    def get_org_name(self, obj):
        parent = obj.parent
        if parent:
            return "{org} ({parent})".format(org=obj.name, parent=parent.name)
        return obj.name

    @admin.display(
        description="Jurisdiction",
        ordering="jurisdiction__name",
    )
    def get_jurisdiction(self, obj):
        jurisdiction = obj.jurisdiction
        if jurisdiction:
            admin_url = reverse(
                "admin:data_jurisdiction_change", args=(jurisdiction.pk,)
            )
            tmpl = '<a href="%s">%s</a>'
            return format_html(tmpl % (admin_url, jurisdiction.name))

        return "(none)"

    list_select_related = ("jurisdiction",)
    list_display = ("get_org_name", "get_jurisdiction", "classification")
    ordering = ("jurisdiction__name", "-classification", "name")
