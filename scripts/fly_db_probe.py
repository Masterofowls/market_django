"""Probe DB host + catalog counts inside the Fly container."""

from __future__ import annotations

import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.db import connection  # noqa: E402

from apps.catalog.models import Category, Product, ProductImage  # noqa: E402

cfg = connection.settings_dict
print("HOST", cfg.get("HOST"))
print("PORT", cfg.get("PORT"))
print("NAME", cfg.get("NAME"))
print("categories", Category.objects.count())
print("products", Product.objects.count())
print("images", ProductImage.objects.count())
