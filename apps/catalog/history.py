"""Recently viewed product tracking."""

from __future__ import annotations

from apps.catalog.models import Product, ProductView


def record_product_view(request, product: Product) -> None:  # noqa: ANN001
    if request.user.is_authenticated:
        view, created = ProductView.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={"session_key": ""},
        )
    else:
        if not request.session.session_key:
            request.session.create()
        view, created = ProductView.objects.get_or_create(
            user=None,
            session_key=request.session.session_key,
            product=product,
        )
    if not created:
        view.view_count += 1
        view.save(update_fields=["view_count", "viewed_at"])


def viewed_products_for(request, *, limit: int = 24) -> list[Product]:  # noqa: ANN001
    if request.user.is_authenticated:
        ids = list(
            ProductView.objects.filter(user=request.user)
            .order_by("-viewed_at")
            .values_list("product_id", flat=True)[:limit]
        )
    else:
        key = request.session.session_key or ""
        if not key:
            return []
        ids = list(
            ProductView.objects.filter(user=None, session_key=key)
            .order_by("-viewed_at")
            .values_list("product_id", flat=True)[:limit]
        )
    if not ids:
        return []
    order = {pk: idx for idx, pk in enumerate(ids)}
    products = list(
        Product.objects.filter(pk__in=ids, is_active=True)
        .select_related("category")
        .prefetch_related("images", "tags")
    )
    products.sort(key=lambda p: order.get(p.pk, 999))
    return products
