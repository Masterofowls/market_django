"""DRF catalog viewsets."""

from __future__ import annotations

from django.db.models import F
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.catalog.filters import ProductFilter
from apps.catalog.models import CatalogSection, Category, Product, ProductShare, Tag
from apps.catalog.serializers import (
    CatalogSectionSerializer,
    CategorySerializer,
    ProductDetailSerializer,
    ProductListSerializer,
    TagSerializer,
)
from apps.recommendations.services import recommend_for_product


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    lookup_field = "slug"
    search_fields = ["name", "slug"]


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = "slug"
    search_fields = ["name", "slug"]


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        Product.objects.filter(is_active=True)
        .select_related("category")
        .prefetch_related("tags", "images")
    )
    filterset_class = ProductFilter
    search_fields = ["name", "sku", "slug", "description", "tags__name", "category__name"]
    ordering_fields = [
        "name",
        "price",
        "discount_percent",
        "average_rating",
        "created_at",
    ]
    lookup_field = "slug"

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ProductDetailSerializer
        return ProductListSerializer

    @action(detail=True, methods=["get"])
    def recommendations(self, request, slug=None):  # noqa: ANN001, ARG002
        product = self.get_object()
        qs = recommend_for_product(product)
        return Response(ProductListSerializer(qs, many=True, context={"request": request}).data)

    @action(detail=True, methods=["post"], permission_classes=[permissions.AllowAny])
    def share(self, request, slug=None):  # noqa: ANN001, ARG002
        product = self.get_object()
        channel = request.data.get("channel", "")
        ProductShare.objects.create(
            product=product,
            channel=channel,
            shared_by=request.user if request.user.is_authenticated else None,
        )
        Product.objects.filter(pk=product.pk).update(share_count=F("share_count") + 1)
        product.refresh_from_db(fields=["share_count"])
        share_url = request.build_absolute_uri(f"/products/{product.slug}/")
        return Response(
            {"share_url": share_url, "share_count": product.share_count},
            status=status.HTTP_201_CREATED,
        )


class CatalogSectionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CatalogSection.objects.filter(is_active=True).prefetch_related(
        "items__product__tags", "items__product__images"
    )
    serializer_class = CatalogSectionSerializer
    lookup_field = "slug"
