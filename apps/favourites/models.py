"""Favourites / wishlist."""

from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.catalog.models import Product


class Favourite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="favourites",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        related_name="favourited_by",
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.user_id} ♥ {self.product_id}"
