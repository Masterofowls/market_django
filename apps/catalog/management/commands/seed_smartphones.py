"""Seed Samsung / Nothing / Apple smartphones with real specs and Wikimedia images."""

from __future__ import annotations

import time
from decimal import Decimal
from pathlib import Path
from urllib.request import Request, urlopen

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from apps.catalog.models import (
    CatalogSection,
    CatalogSectionItem,
    Category,
    Product,
    ProductImage,
    Tag,
)
from apps.marketing.models import Banner

USER_AGENT = "ElectroMarketSeeder/1.0 (educational catalog; +https://localhost)"


PRODUCTS = [
    {
        "brand": "Samsung",
        "name": "Samsung Galaxy S25 Ultra",
        "sku": "SAM-S25U-256",
        "price": "1299.00",
        "discount": "5.00",
        "stock": 24,
        "featured": True,
        "short": "Flagship Ultra with 200MP camera, S Pen, and titanium frame.",
        "specs": {
            "Display": "6.9-inch Dynamic AMOLED 2X, 120Hz, QHD+",
            "Chipset": "Snapdragon 8 Elite for Galaxy",
            "RAM / Storage": "12 GB / 256 GB",
            "Rear cameras": "200 MP + 50 MP + 50 MP + 10 MP",
            "Front camera": "12 MP",
            "Battery": "5000 mAh, 45W wired",
            "OS": "Android 15, One UI 7",
            "Build": "Titanium frame, Gorilla Armor 2",
            "IP rating": "IP68",
        },
        "tags": ["samsung", "flagship", "5g", "s-pen", "android"],
        "image": "https://commons.wikimedia.org/wiki/Special:FilePath/Samsung_Galaxy_S25_Ultra.jpg",
    },
    {
        "brand": "Samsung",
        "name": "Samsung Galaxy S25",
        "sku": "SAM-S25-256",
        "price": "799.00",
        "discount": "8.00",
        "stock": 40,
        "featured": True,
        "short": "Compact Galaxy flagship with pro-grade cameras and Galaxy AI.",
        "specs": {
            "Display": "6.2-inch Dynamic AMOLED 2X, 120Hz",
            "Chipset": "Snapdragon 8 Elite for Galaxy",
            "RAM / Storage": "12 GB / 256 GB",
            "Rear cameras": "50 MP + 12 MP + 10 MP",
            "Front camera": "12 MP",
            "Battery": "4000 mAh, 25W wired",
            "OS": "Android 15, One UI 7",
            "Build": "Armor aluminum, Gorilla Glass Victus 2",
            "IP rating": "IP68",
        },
        "tags": ["samsung", "flagship", "5g", "compact", "android"],
        "image": (
            "https://commons.wikimedia.org/wiki/Special:FilePath/"
            "Galaxy_S25_Black_(front).png"
        ),
    },
    {
        "brand": "Samsung",
        "name": "Samsung Galaxy Z Flip6",
        "sku": "SAM-ZFLIP6-256",
        "price": "1099.00",
        "discount": "10.00",
        "stock": 18,
        "featured": False,
        "short": "Foldable clamshell with FlexCam and a brighter cover screen.",
        "specs": {
            "Display": "6.7-inch AMOLED main + 3.4-inch cover, 120Hz",
            "Chipset": "Snapdragon 8 Gen 3 for Galaxy",
            "RAM / Storage": "12 GB / 256 GB",
            "Rear cameras": "50 MP + 12 MP",
            "Front camera": "10 MP",
            "Battery": "4000 mAh, 25W wired",
            "OS": "Android 14, One UI 6.1.1",
            "Build": "Armor aluminum, hinge protection",
            "IP rating": "IP48",
        },
        "tags": ["samsung", "foldable", "5g", "android"],
        "image": (
            "https://commons.wikimedia.org/wiki/Special:FilePath/"
            "Samsung_Galaxy_Z_Flip_6.jpg"
        ),
    },
    {
        "brand": "Nothing",
        "name": "Nothing Phone (2a)",
        "sku": "NOT-P2A-256",
        "price": "349.00",
        "discount": "12.00",
        "stock": 55,
        "featured": True,
        "short": "Glyph interface midranger with clean Nothing OS design.",
        "specs": {
            "Display": "6.7-inch AMOLED, 120Hz, flexible LTPO",
            "Chipset": "MediaTek Dimensity 7200 Pro",
            "RAM / Storage": "8 GB / 256 GB",
            "Rear cameras": "50 MP (OIS) + 50 MP ultrawide",
            "Front camera": "32 MP",
            "Battery": "5000 mAh, 45W wired",
            "OS": "Nothing OS 2.5 (Android 14)",
            "Build": "Plastic unibody, Glyph LED matrix",
            "IP rating": "IP54",
        },
        "tags": ["nothing", "midrange", "5g", "glyph", "android"],
        "image": "https://commons.wikimedia.org/wiki/Special:FilePath/Nothing_phone_(2a).jpg",
    },
    {
        "brand": "Nothing",
        "name": "Nothing Phone (2)",
        "sku": "NOT-P2-256",
        "price": "599.00",
        "discount": "15.00",
        "stock": 32,
        "featured": True,
        "short": "Glyph phone with Snapdragon 8+ Gen 1 and dual 50MP cameras.",
        "specs": {
            "Display": "6.7-inch LTPO OLED, 120Hz, 2412×1080",
            "Chipset": "Snapdragon 8+ Gen 1",
            "RAM / Storage": "12 GB / 256 GB",
            "Rear cameras": "50 MP (OIS) + 50 MP ultrawide",
            "Front camera": "32 MP",
            "Battery": "4700 mAh, 45W wired / 15W wireless",
            "OS": "Nothing OS 2.5 (Android 14)",
            "Build": "Glass front/back, aluminum frame, Glyph Interface",
            "IP rating": "IP54",
        },
        "tags": ["nothing", "flagship", "5g", "glyph", "android"],
        "image": (
            "https://commons.wikimedia.org/wiki/Special:FilePath/"
            "Nothing_phone_(2)_(Booredatwork.com)_013.png"
        ),
    },
    {
        "brand": "Nothing",
        "name": "Nothing Phone (2a) Plus",
        "sku": "NOT-P2AP-256",
        "price": "399.00",
        "discount": "7.00",
        "stock": 28,
        "featured": False,
        "short": "2a Plus upgrade with brighter display and 50MP front camera.",
        "specs": {
            "Display": "6.7-inch AMOLED, 120Hz, up to 1300 nits",
            "Chipset": "MediaTek Dimensity 7200 Pro",
            "RAM / Storage": "12 GB / 256 GB",
            "Rear cameras": "50 MP (OIS) + 50 MP ultrawide",
            "Front camera": "50 MP",
            "Battery": "5000 mAh, 50W wired",
            "OS": "Nothing OS 2.6 (Android 14)",
            "Build": "Refined Glyph lighting, plastic unibody",
            "IP rating": "IP54",
        },
        "tags": ["nothing", "midrange", "5g", "glyph", "android"],
        # Reuse 2a photo when a dedicated Commons still is unavailable.
        "image": "https://commons.wikimedia.org/wiki/Special:FilePath/Nothing_phone_(2a).jpg",
    },
    {
        "brand": "Apple",
        "name": "Apple iPhone 16 Pro",
        "sku": "APL-IP16P-256",
        "price": "999.00",
        "discount": "0.00",
        "stock": 30,
        "featured": True,
        "short": "Titanium Pro iPhone with Camera Control and A18 Pro.",
        "specs": {
            "Display": "6.3-inch Super Retina XDR OLED, 120Hz ProMotion",
            "Chipset": "Apple A18 Pro",
            "RAM / Storage": "8 GB / 256 GB",
            "Rear cameras": "48 MP Fusion + 12 MP Ultra Wide + 12 MP 5x Telephoto",
            "Front camera": "12 MP",
            "Battery": "Up to 27 hours video playback",
            "OS": "iOS 18",
            "Build": "Grade 5 titanium, Ceramic Shield",
            "IP rating": "IP68",
        },
        "tags": ["apple", "iphone", "flagship", "5g", "ios"],
        "image": "https://commons.wikimedia.org/wiki/Special:FilePath/IPhone_16_Pro_(54251031612).jpg",
    },
    {
        "brand": "Apple",
        "name": "Apple iPhone 16 Pro Max",
        "sku": "APL-IP16PM-256",
        "price": "1199.00",
        "discount": "3.00",
        "stock": 22,
        "featured": True,
        "short": "Largest Pro iPhone with longest battery life and 5x tetraprism zoom.",
        "specs": {
            "Display": "6.9-inch Super Retina XDR OLED, 120Hz ProMotion",
            "Chipset": "Apple A18 Pro",
            "RAM / Storage": "8 GB / 256 GB",
            "Rear cameras": "48 MP Fusion + 12 MP Ultra Wide + 12 MP 5x Telephoto",
            "Front camera": "12 MP",
            "Battery": "Up to 33 hours video playback",
            "OS": "iOS 18",
            "Build": "Grade 5 titanium, Ceramic Shield",
            "IP rating": "IP68",
        },
        "tags": ["apple", "iphone", "flagship", "5g", "ios"],
        "image": (
            "https://commons.wikimedia.org/wiki/Special:FilePath/"
            "IPhone_16_Pro_Max_(54252162478).jpg"
        ),
    },
    {
        "brand": "Apple",
        "name": "Apple iPhone 16",
        "sku": "APL-IP16-128",
        "price": "799.00",
        "discount": "6.00",
        "stock": 45,
        "featured": False,
        "short": "A18-powered iPhone 16 with Camera Control and dual Fusion cameras.",
        "specs": {
            "Display": "6.1-inch Super Retina XDR OLED, 60Hz",
            "Chipset": "Apple A18",
            "RAM / Storage": "8 GB / 128 GB",
            "Rear cameras": "48 MP Fusion + 12 MP Ultra Wide",
            "Front camera": "12 MP",
            "Battery": "Up to 22 hours video playback",
            "OS": "iOS 18",
            "Build": "Aluminum design, Ceramic Shield",
            "IP rating": "IP68",
        },
        "tags": ["apple", "iphone", "5g", "ios"],
        "image": "https://commons.wikimedia.org/wiki/Special:FilePath/IPhone_16_Pro_series.jpg",
    },
]


def _format_description(short: str, specs: dict[str, str]) -> str:
    lines = [short, "", "Key specifications:"]
    for key, value in specs.items():
        lines.append(f"• {key}: {value}")
    lines.append("")
    lines.append(
        "Images sourced from Wikimedia Commons for catalog demonstration "
        "(see file pages for license details)."
    )
    return "\n".join(lines)


def _download(url: str) -> tuple[bytes, str]:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=60) as response:  # noqa: S310
        data = response.read()
        content_type = response.headers.get_content_type()
    ext = ".jpg"
    if "png" in content_type or url.lower().endswith(".png"):
        ext = ".png"
    elif "webp" in content_type:
        ext = ".webp"
    return data, ext


class Command(BaseCommand):
    help = "Seed smartphone catalog (Samsung, Nothing, Apple) with real images."

    def add_arguments(self, parser):  # noqa: ANN001
        parser.add_argument(
            "--force",
            action="store_true",
            help="Replace existing seeded SKUs and refresh images.",
        )

    @transaction.atomic
    def handle(self, *args, **options):  # noqa: ANN002, ANN003
        force = options["force"]
        phones = Category.objects.get_or_create(
            slug="smartphones",
            defaults={
                "name": "Smartphones",
                "description": "Latest smartphones from Samsung, Nothing, and Apple.",
            },
        )[0]

        brand_categories: dict[str, Category] = {}
        header_orders = {"Samsung": 10, "Nothing": 20, "Apple": 30}
        for brand in ("Samsung", "Nothing", "Apple"):
            category, _ = Category.objects.get_or_create(
                slug=slugify(brand),
                defaults={
                    "name": brand,
                    "parent": phones,
                    "description": f"{brand} smartphones",
                    "show_in_header": True,
                    "header_order": header_orders[brand],
                },
            )
            if not category.show_in_header:
                category.show_in_header = True
                category.header_order = header_orders[brand]
                category.parent = category.parent or phones
                category.save(
                    update_fields=["show_in_header", "header_order", "parent", "updated_at"]
                )
            brand_categories[brand] = category

        section, _ = CatalogSection.objects.get_or_create(
            slug="flagship-picks",
            defaults={
                "title": "Flagship picks",
                "subtitle": "Editor selections across Samsung, Nothing, and Apple",
                "sort_order": 1,
                "is_active": True,
            },
        )

        Banner.objects.get_or_create(
            title="New season smartphones",
            defaults={
                "subtitle": "Compare Samsung, Nothing, and Apple side by side",
                "link_url": "/products/?category=smartphones",
                "is_active": True,
                "sort_order": 1,
            },
        )

        created = 0
        updated = 0
        for idx, item in enumerate(PRODUCTS):
            category = brand_categories[item["brand"]]
            defaults = {
                "name": item["name"],
                "slug": slugify(item["name"]),
                "short_description": item["short"],
                "description": _format_description(item["short"], item["specs"]),
                "category": category,
                "price": Decimal(item["price"]),
                "discount_percent": Decimal(item["discount"]),
                "stock": item["stock"],
                "is_active": True,
                "is_featured": item["featured"],
            }
            product, was_created = Product.objects.update_or_create(
                sku=item["sku"],
                defaults=defaults,
            )
            created += int(was_created)
            updated += int(not was_created)

            tag_objs = []
            for tag_name in item["tags"]:
                tag, _ = Tag.objects.get_or_create(
                    slug=slugify(tag_name),
                    defaults={"name": tag_name.replace("-", " ").title()},
                )
                tag_objs.append(tag)
            product.tags.set(tag_objs)

            CatalogSectionItem.objects.get_or_create(
                section=section,
                product=product,
                defaults={"sort_order": idx},
            )

            needs_image = force or not product.images.exists()
            if needs_image:
                product.images.all().delete()
                try:
                    time.sleep(1.5)
                    payload, ext = _download(item["image"])
                    filename = f"{product.slug}{ext}"
                    image = ProductImage(
                        product=product,
                        alt_text=product.name,
                        is_primary=True,
                    )
                    image.image.save(filename, ContentFile(payload), save=True)
                    self.stdout.write(self.style.SUCCESS(f"Image OK  {product.name}"))
                except Exception as exc:  # noqa: BLE001
                    self.stdout.write(
                        self.style.WARNING(f"Image FAIL {product.name}: {exc}")
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed complete. created={created} updated={updated} "
                f"media={Path('media').resolve()}"
            )
        )
