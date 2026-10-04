"""Shopping cart models."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models

from apps.catalog.models import Product


class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
        null=True,
        blank=True,
    )
    session_key = models.CharField(max_length=64, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        owner = self.user_id or self.session_key or "anon"
        return f"Cart({owner})"

    @property
    def subtotal(self) -> Decimal:
        return sum(
            (item.line_total for item in self.items.select_related("product")), Decimal("0.00")
        )

    @property
    def item_count(self) -> int:
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name="cart_items", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        unique_together = ("cart", "product")

    def __str__(self) -> str:
        return f"{self.product} x {self.quantity}"

    def save(self, *args, **kwargs):  # noqa: ANN002, ANN003
        if self.product_id and (self.unit_price is None or self.unit_price == 0):
            self.unit_price = self.product.final_price
        super().save(*args, **kwargs)

    @property
    def line_total(self) -> Decimal:
        return (self.unit_price * self.quantity).quantize(Decimal("0.01"))
