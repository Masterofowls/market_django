"""DRF serializers for catalog."""

from __future__ import annotations

from rest_framework import serializers

from apps.catalog.models import (
    CatalogSection,
    CatalogSectionItem,
    Category,
    Product,
    ProductImage,
    Tag,
)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "slug")


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug", "parent", "description", "is_active")


class ProductImageSerializer(serializers.ModelSerializer):
    preview_url = serializers.SerializerMethodField()
    card_thumb_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = (
            "id",
            "image",
            "alt_text",
            "sort_order",
            "is_primary",
            "preview_url",
            "card_thumb_url",
        )

    def get_preview_url(self, obj: ProductImage) -> str | None:
        try:
            return obj.preview.url
        except Exception:  # noqa: BLE001
            return None

    def get_card_thumb_url(self, obj: ProductImage) -> str | None:
        try:
            return obj.card_thumb.url
        except Exception:  # noqa: BLE001
            return None


class ProductListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    final_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    primary_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "slug",
            "sku",
            "short_description",
            "category",
            "tags",
            "price",
            "discount_percent",
            "final_price",
            "stock",
            "is_active",
            "is_featured",
            "average_rating",
            "rating_count",
            "share_count",
            "primary_image",
        )

    def get_primary_image(self, obj: Product) -> dict | None:
        image = obj.images.filter(is_primary=True).first() or obj.images.first()
        if not image:
            return None
        return ProductImageSerializer(image, context=self.context).data


class ProductDetailSerializer(ProductListSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    description = serializers.CharField()

    class Meta(ProductListSerializer.Meta):
        fields = ProductListSerializer.Meta.fields + ("description", "images", "created_at")


class CatalogSectionItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)

    class Meta:
        model = CatalogSectionItem
        fields = ("id", "product", "sort_order")


class CatalogSectionSerializer(serializers.ModelSerializer):
    items = CatalogSectionItemSerializer(many=True, read_only=True)

    class Meta:
        model = CatalogSection
        fields = ("id", "title", "slug", "subtitle", "is_active", "sort_order", "items")
