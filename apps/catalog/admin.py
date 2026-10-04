"""Catalog admin with CSV import/export and section management."""

from __future__ import annotations

from django.contrib import admin
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget

from apps.catalog.models import (
    CatalogSection,
    CatalogSectionItem,
    Category,
    Product,
    ProductImage,
    ProductShare,
    Tag,
)


class CategoryResource(resources.ModelResource):
    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "slug",
            "parent",
            "description",
            "is_active",
            "show_in_header",
            "header_order",
        )
        import_id_fields = ("slug",)


class TagResource(resources.ModelResource):
    class Meta:
        model = Tag
        fields = ("id", "name", "slug")
        import_id_fields = ("slug",)


class ProductResource(resources.ModelResource):
    category = fields.Field(
        column_name="category",
        attribute="category",
        widget=ForeignKeyWidget(Category, "slug"),
    )
    tags = fields.Field(
        column_name="tags",
        attribute="tags",
        widget=ManyToManyWidget(Tag, field="slug", separator="|"),
    )

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "slug",
            "sku",
            "short_description",
            "description",
            "category",
            "tags",
            "price",
            "discount_percent",
            "stock",
            "is_active",
            "is_featured",
        )
        import_id_fields = ("sku",)
        skip_unchanged = True


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class CatalogSectionItemInline(admin.TabularInline):
    model = CatalogSectionItem
    extra = 1
    autocomplete_fields = ("product",)


@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin):
    resource_classes = [CategoryResource]
    list_display = (
        "name",
        "slug",
        "parent",
        "is_active",
        "show_in_header",
        "header_order",
    )
    list_editable = ("show_in_header", "header_order", "is_active")
    list_filter = ("is_active", "show_in_header", "parent")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("header_order", "name")
    fieldsets = (
        (None, {"fields": ("name", "slug", "parent", "description", "is_active")}),
        (
            "Header navigation",
            {
                "fields": ("show_in_header", "header_order"),
                "description": (
                    "Enable Show in header to display this category next to Catalog "
                    "(e.g. Samsung, Huawei). Uncheck to remove it from the header."
                ),
            },
        ),
    )


@admin.register(Tag)
class TagAdmin(ImportExportModelAdmin):
    resource_classes = [TagResource]
    list_display = ("name", "slug")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    resource_classes = [ProductResource]
    list_display = (
        "name",
        "sku",
        "category",
        "price",
        "discount_percent",
        "stock",
        "is_active",
        "is_featured",
        "average_rating",
    )
    list_filter = ("is_active", "is_featured", "category", "tags")
    search_fields = ("name", "sku", "slug", "description", "tags__name")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("tags",)
    inlines = [ProductImageInline]
    autocomplete_fields = ("category",)


@admin.register(CatalogSection)
class CatalogSectionAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_active", "sort_order")
    list_filter = ("is_active",)
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [CatalogSectionItemInline]


@admin.register(ProductShare)
class ProductShareAdmin(admin.ModelAdmin):
    list_display = ("product", "channel", "shared_by", "created_at")
    list_filter = ("channel",)
    search_fields = ("product__name", "channel")
