"""User admin with CSV import/export."""

from __future__ import annotations

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from apps.accounts.models import User


class UserResource(resources.ModelResource):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "is_active",
            "is_staff",
            "date_joined",
            "marketing_opt_in",
        )
        import_id_fields = ("email",)
        skip_unchanged = True
        report_skipped = True


@admin.register(User)
class UserAdmin(ImportExportModelAdmin, DjangoUserAdmin):
    resource_classes = [UserResource]
    list_display = (
        "username",
        "email",
        "phone",
        "is_staff",
        "is_active",
        "date_joined",
    )
    list_filter = ("is_staff", "is_active", "marketing_opt_in")
    search_fields = ("username", "email", "first_name", "last_name", "phone")
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Marketplace", {"fields": ("phone", "marketing_opt_in")}),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ("Marketplace", {"fields": ("phone", "marketing_opt_in")}),
    )
