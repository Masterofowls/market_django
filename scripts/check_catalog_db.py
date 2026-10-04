"""Print catalog counts and connection target (Supabase/Fly)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.db import connection  # noqa: E402

from apps.catalog.models import Category, Product, ProductImage, Tag  # noqa: E402


def main() -> None:
    cfg = connection.settings_dict
    print(f"ENGINE={cfg.get('ENGINE')}")
    print(f"HOST={cfg.get('HOST')}")
    print(f"PORT={cfg.get('PORT')}")
    print(f"NAME={cfg.get('NAME')}")
    print(f"categories={Category.objects.count()}")
    for c in Category.objects.all().order_by("name"):
        print(f"  category: {c.name} slug={c.slug} products={c.products.count()}")
    print(f"tags={Tag.objects.count()}")
    print(f"products={Product.objects.count()}")
    print(f"images={ProductImage.objects.count()}")
    for p in (
        Product.objects.select_related("category")
        .prefetch_related("images")
        .order_by("name")
    ):
        cat = p.category.name if p.category_id else "?"
        imgs = list(p.images.all())
        print(
            f"  product: {p.name} | {cat} | imgs={len(imgs)} "
            f"stock={p.stock} price={p.price}"
        )
        for im in imgs:
            name = im.image.name if im.image else None
            print(f"    image: {name}")


if __name__ == "__main__":
    main()
