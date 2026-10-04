"""In-app notifications."""

from __future__ import annotations

from django.conf import settings
from django.db import models


class Notification(models.Model):
    class Kind(models.TextChoices):
        INFO = "info", "Info"
        ORDER = "order", "Order"
        PROMO = "promo", "Promo"
        SYSTEM = "system", "System"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="notifications",
        on_delete=models.CASCADE,
    )
    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.INFO)
    title = models.CharField(max_length=160)
    body = models.TextField(blank=True)
    link_url = models.CharField(max_length=500, blank=True)
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title
