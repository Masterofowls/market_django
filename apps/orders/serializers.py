"""Order serializers."""

from __future__ import annotations

from rest_framework import serializers

from apps.orders.models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = (
            "id",
            "product",
            "product_name",
            "product_sku",
            "quantity",
            "unit_price",
            "line_total",
        )


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "number",
            "email",
            "status",
            "subtotal",
            "discount_total",
            "shipping_total",
            "grand_total",
            "shipping_address",
            "notes",
            "items",
            "created_at",
        )
        read_only_fields = (
            "number",
            "status",
            "subtotal",
            "discount_total",
            "shipping_total",
            "grand_total",
            "created_at",
        )


class CheckoutSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, allow_blank=True)
    shipping_address = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)
