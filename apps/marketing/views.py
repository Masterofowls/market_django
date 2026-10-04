from __future__ import annotations

from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets

from apps.marketing.models import Banner, Slider
from apps.marketing.serializers import BannerSerializer, SliderSerializer


class BannerViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BannerSerializer

    def get_queryset(self):
        now = timezone.now()
        return (
            Banner.objects.filter(is_active=True)
            .filter(Q(starts_at__isnull=True) | Q(starts_at__lte=now))
            .filter(Q(ends_at__isnull=True) | Q(ends_at__gte=now))
        )


class SliderViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Slider.objects.filter(is_active=True).prefetch_related("images")
    serializer_class = SliderSerializer
    lookup_field = "slug"
