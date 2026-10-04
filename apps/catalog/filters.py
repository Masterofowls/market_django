"""Catalog filterset: name, category, id, tag, price, discount."""

from __future__ import annotations

import django_filters

from apps.catalog.models import Product


class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    q = django_filters.CharFilter(method="filter_q")
    category = django_filters.NumberFilter(field_name="category_id")
    category_slug = django_filters.CharFilter(field_name="category__slug")
    tag = django_filters.CharFilter(method="filter_tag")
    tag_id = django_filters.NumberFilter(field_name="tags__id")
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    min_discount = django_filters.NumberFilter(
        field_name="discount_percent",
        lookup_expr="gte",
    )
    featured = django_filters.BooleanFilter(field_name="is_featured")
    in_stock = django_filters.BooleanFilter(method="filter_in_stock")

    class Meta:
        model = Product
        fields = ["id", "sku", "is_active"]

    def filter_q(self, queryset, name, value):  # noqa: ANN001, ARG002
        from django.db.models import Q

        query = (value or "").strip()
        if not query:
            return queryset
        filters = (
            Q(name__icontains=query)
            | Q(sku__icontains=query)
            | Q(slug__icontains=query)
            | Q(short_description__icontains=query)
        )
        if query.isdigit():
            filters |= Q(pk=int(query))
        return queryset.filter(filters).distinct()

    def filter_tag(self, queryset, name, value):  # noqa: ANN001, ARG002
        return queryset.filter(tags__slug__iexact=value) | queryset.filter(
            tags__name__icontains=value
        )

    def filter_in_stock(self, queryset, name, value):  # noqa: ANN001, ARG002
        if value:
            return queryset.filter(stock__gt=0)
        return queryset.filter(stock=0)
