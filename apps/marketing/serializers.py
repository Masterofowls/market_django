from __future__ import annotations

from rest_framework import serializers

from apps.marketing.models import Banner, Slider, SliderImage


class BannerSerializer(serializers.ModelSerializer):
    preview_url = serializers.SerializerMethodField()

    class Meta:
        model = Banner
        fields = (
            "id",
            "title",
            "subtitle",
            "image",
            "preview_url",
            "link_url",
            "sort_order",
        )

    def get_preview_url(self, obj: Banner) -> str | None:
        if not obj.image:
            return None
        try:
            return obj.preview.url
        except Exception:  # noqa: BLE001
            return None


class SliderImageSerializer(serializers.ModelSerializer):
    preview_url = serializers.SerializerMethodField()

    class Meta:
        model = SliderImage
        fields = ("id", "image", "preview_url", "caption", "link_url", "sort_order")

    def get_preview_url(self, obj: SliderImage) -> str | None:
        try:
            return obj.preview.url
        except Exception:  # noqa: BLE001
            return None


class SliderSerializer(serializers.ModelSerializer):
    images = SliderImageSerializer(many=True, read_only=True)

    class Meta:
        model = Slider
        fields = ("id", "name", "slug", "images")
