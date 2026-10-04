"""Catalog: categories, tags, products, sections, share tracking."""

from __future__ import annotations

from decimal import Decimal

from django.db import models
from django.utils.text import slugify
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill, ResizeToFit


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.CASCADE,
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    show_in_header = models.BooleanField(
        default=False,
        help_text="Show this category in the site header navigation.",
    )
    header_order = models.PositiveIntegerField(
        default=0,
        help_text="Lower numbers appear first in the header (left to right).",
    )

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["show_in_header", "header_order"]),
        ]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):  # noqa: ANN002, ANN003
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Tag(TimeStampedModel):
    name = models.CharField(max_length=64, unique=True)
    slug = models.SlugField(max_length=80, unique=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):  # noqa: ANN002, ANN003
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(TimeStampedModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    sku = models.CharField(max_length=64, unique=True, blank=True)
    description = models.TextField(blank=True)
    short_description = models.CharField(max_length=500, blank=True)
    category = models.ForeignKey(
        Category,
        related_name="products",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="products")
    price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Percent off list price (0-100).",
    )
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    rating_count = models.PositiveIntegerField(default=0)
    share_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["sku"]),
            models.Index(fields=["is_active", "is_featured"]),
        ]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):  # noqa: ANN002, ANN003
        if not self.slug:
            base = slugify(self.name) or "product"
            candidate = base
            idx = 1
            while Product.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base}-{idx}"
                idx += 1
            self.slug = candidate
        if not self.sku:
            self.sku = f"SKU-{self.slug[:40]}".upper()
        super().save(*args, **kwargs)

    @property
    def final_price(self) -> Decimal:
        if self.discount_percent <= 0:
            return self.price
        discount = (self.price * self.discount_percent) / Decimal("100")
        return (self.price - discount).quantize(Decimal("0.01"))


class ProductImage(TimeStampedModel):
    product = models.ForeignKey(
        Product,
        related_name="images",
        on_delete=models.CASCADE,
    )
    image = models.ImageField(upload_to="products/%Y/%m/")
    alt_text = models.CharField(max_length=255, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_primary = models.BooleanField(default=False)

    preview = ImageSpecField(
        source="image",
        processors=[ResizeToFit(640, 640)],
        format="JPEG",
        options={"quality": 85},
    )
    card_thumb = ImageSpecField(
        source="image",
        processors=[ResizeToFill(360, 360)],
        format="JPEG",
        options={"quality": 80},
    )

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self) -> str:
        return f"{self.product_id} image {self.pk}"


class CatalogSection(TimeStampedModel):
    """Admin-managed storefront section (e.g. New Arrivals, Deals)."""

    title = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    subtitle = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "title"]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):  # noqa: ANN002, ANN003
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class CatalogSectionItem(models.Model):
    section = models.ForeignKey(
        CatalogSection,
        related_name="items",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        related_name="section_items",
        on_delete=models.CASCADE,
    )
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]
        unique_together = ("section", "product")

    def __str__(self) -> str:
        return f"{self.section} → {self.product}"


class ProductShare(TimeStampedModel):
    product = models.ForeignKey(
        Product,
        related_name="shares",
        on_delete=models.CASCADE,
    )
    channel = models.CharField(max_length=64, blank=True)
    shared_by = models.ForeignKey(
        "accounts.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="product_shares",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Share {self.product_id} via {self.channel or 'link'}"


class ProductView(models.Model):
    """Recently viewed products for guests (session) and signed-in users."""

    user = models.ForeignKey(
        "accounts.User",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="product_views",
    )
    session_key = models.CharField(max_length=64, blank=True, db_index=True)
    product = models.ForeignKey(
        Product,
        related_name="views",
        on_delete=models.CASCADE,
    )
    viewed_at = models.DateTimeField(auto_now=True)
    view_count = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["-viewed_at"]
        indexes = [
            models.Index(fields=["user", "-viewed_at"]),
            models.Index(fields=["session_key", "-viewed_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"],
                condition=models.Q(user__isnull=False),
                name="uniq_product_view_user",
            ),
            models.UniqueConstraint(
                fields=["session_key", "product"],
                condition=models.Q(user__isnull=True),
                name="uniq_product_view_session",
            ),
        ]

    def __str__(self) -> str:
        owner = self.user_id or self.session_key or "anon"
        return f"View({owner} → {self.product_id})"
