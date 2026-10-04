"""Favourite serializers."""

from __future__ import annotations

from rest_framework import serializers

from apps.catalog.serializers import ProductListSerializer
from apps.favourites.models import Favourite


class FavouriteSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Favourite
        fields = ("id", "product", "product_id", "created_at")
        read_only_fields = ("created_at",)
