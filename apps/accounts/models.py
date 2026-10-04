"""Custom user model for marketplace accounts."""

from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Storefront user with optional profile fields."""

    phone = models.CharField(max_length=32, blank=True)
    marketing_opt_in = models.BooleanField(default=False)

    class Meta:
        ordering = ["username"]

    def __str__(self) -> str:
        return self.get_username()
