"""Keep product rating aggregates in sync."""

from __future__ import annotations

from decimal import Decimal

from django.db.models import Avg, Count
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.catalog.models import Product
from apps.reviews.models import Review


def _refresh_product_rating(product_id: int) -> None:
    stats = Review.objects.filter(product_id=product_id, is_approved=True).aggregate(
        avg=Avg("rating"),
        count=Count("id"),
    )
    Product.objects.filter(pk=product_id).update(
        average_rating=Decimal(stats["avg"] or 0).quantize(Decimal("0.01")),
        rating_count=stats["count"] or 0,
    )


@receiver(post_save, sender=Review)
def review_saved(sender, instance: Review, **kwargs):  # noqa: ANN001, ARG001
    _refresh_product_rating(instance.product_id)


@receiver(post_delete, sender=Review)
def review_deleted(sender, instance: Review, **kwargs):  # noqa: ANN001, ARG001
    _refresh_product_rating(instance.product_id)
