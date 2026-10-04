"""Banners and image sliders."""

from __future__ import annotations

from django.db import models
from django.utils.text import slugify
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill


class Banner(models.Model):
    title = models.CharField(max_length=160)
    subtitle = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to="banners/%Y/%m/", blank=True)
    link_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    preview = ImageSpecField(
        source="image",
        processors=[ResizeToFill(1400, 420)],
        format="JPEG",
        options={"quality": 85},
    )

    class Meta:
        ordering = ["sort_order", "-created_at"]

    def __str__(self) -> str:
        return self.title


class Slider(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):  # noqa: ANN002, ANN003
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class SliderImage(models.Model):
    slider = models.ForeignKey(Slider, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="sliders/%Y/%m/")
    caption = models.CharField(max_length=255, blank=True)
    link_url = models.URLField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    preview = ImageSpecField(
        source="image",
        processors=[ResizeToFill(1600, 600)],
        format="JPEG",
        options={"quality": 85},
    )

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self) -> str:
        return f"{self.slider} #{self.sort_order}"
