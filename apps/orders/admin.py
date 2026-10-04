"""Order admin with CSV import/export."""

from __future__ import annotations

from django.contrib import admin
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget

from apps.accounts.models import User
from apps.orders.models import Order, OrderItem


class OrderResource(resources.ModelResource):
    user = fields.Field(
        column_name="user_email",
        attribute="user",
        widget=ForeignKeyWidget(User, "email"),
    )

    class Meta:
        model = Order
        fields = (
            "id",
            "number",
            "user",
            "email",
            "status",
            "subtotal",
            "discount_total",
            "shipping_total",
            "grand_total",
            "shipping_address",
            "notes",
            "created_at",
        )
        import_id_fields = ("number",)
        skip_unchanged = True


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("line_total",)


@admin.register(Order)
class OrderAdmin(ImportExportModelAdmin):
    resource_classes = [OrderResource]
    list_display = (
        "number",
        "email",
        "status",
        "grand_total",
        "created_at",
    )
    list_filter = ("status",)
    search_fields = ("number", "email", "user__username", "user__email")
    inlines = [OrderItemInline]
    readonly_fields = ("number", "subtotal", "grand_total", "created_at", "updated_at")
