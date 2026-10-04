"""Recommendation and suggestion helpers."""

from __future__ import annotations

import re

from django.db.models import Case, Count, IntegerField, Q, QuerySet, When

from apps.catalog.models import Product

_STOPWORDS = {
    "a",
    "an",
    "and",
    "the",
    "with",
    "from",
    "for",
    "of",
    "to",
    "in",
    "on",
    "by",
    "is",
    "are",
    "this",
    "that",
    "key",
    "specifications",
    "images",
    "sourced",
    "wikimedia",
    "commons",
    "catalog",
    "demonstration",
    "see",
    "file",
    "pages",
    "license",
    "details",
}


def _description_terms(product: Product, limit: int = 8) -> list[str]:
    text = f"{product.short_description} {product.description}"
    tokens = re.findall(r"[A-Za-z0-9+]{3,}", text.lower())
    terms: list[str] = []
    for token in tokens:
        if token in _STOPWORDS or token.isdigit():
            continue
        if token not in terms:
            terms.append(token)
        if len(terms) >= limit:
            break
    return terms


def recommend_for_product(product: Product, limit: int = 8) -> QuerySet[Product]:
    """Suggest related products by shared category, tags, and description terms."""
    tag_ids = list(product.tags.values_list("id", flat=True))
    terms = _description_terms(product)
    qs = (
        Product.objects.filter(is_active=True)
        .exclude(pk=product.pk)
        .select_related("category")
        .prefetch_related("images", "tags")
    )

    relevance = Q(pk__in=[])
    if product.category_id:
        relevance |= Q(category_id=product.category_id)
        relevance |= Q(category__parent_id=product.category.parent_id)
    if tag_ids:
        relevance |= Q(tags__in=tag_ids)
    for term in terms:
        relevance |= Q(name__icontains=term) | Q(short_description__icontains=term)

    qs = qs.filter(relevance).distinct()
    qs = qs.annotate(
        shared_tags=Count("tags", filter=Q(tags__in=tag_ids)),
        same_category=Case(
            When(category_id=product.category_id, then=1),
            default=0,
            output_field=IntegerField(),
        ),
    ).order_by("-shared_tags", "-same_category", "-is_featured", "-average_rating", "name")
    return qs[:limit]


def suggest_products(
    *,
    query: str = "",
    category_id: int | None = None,
    tag: str = "",
    limit: int = 12,
) -> QuerySet[Product]:
    """Lightweight suggestions for search boxes / autocomplete."""
    qs = Product.objects.filter(is_active=True)
    if category_id:
        qs = qs.filter(category_id=category_id)
    if tag:
        qs = qs.filter(Q(tags__slug__iexact=tag) | Q(tags__name__icontains=tag))
    if query:
        filters = (
            Q(name__icontains=query)
            | Q(sku__icontains=query)
            | Q(slug__icontains=query)
            | Q(description__icontains=query)
            | Q(tags__name__icontains=query)
        )
        if query.isdigit():
            filters |= Q(pk=int(query))
        qs = qs.filter(filters).distinct()
    return qs.order_by("-is_featured", "-average_rating", "name")[:limit]


def recommend_for_user(user, limit: int = 12) -> QuerySet[Product]:  # noqa: ANN001
    """Personalize from favourites + past order categories/tags."""
    from apps.favourites.models import Favourite
    from apps.orders.models import OrderItem

    fav_ids = list(Favourite.objects.filter(user=user).values_list("product_id", flat=True)[:50])
    ordered = OrderItem.objects.filter(order__user=user).select_related("product")[:100]
    category_ids = {i.product.category_id for i in ordered if i.product and i.product.category_id}
    tag_ids: set[int] = set()
    for item in ordered:
        if item.product_id:
            tag_ids.update(item.product.tags.values_list("id", flat=True))

    qs = Product.objects.filter(is_active=True).exclude(pk__in=fav_ids)
    if category_ids or tag_ids:
        qs = qs.filter(Q(category_id__in=category_ids) | Q(tags__in=tag_ids)).distinct()
    else:
        qs = qs.filter(is_featured=True)
    return qs.order_by("-average_rating", "-created_at")[:limit]
