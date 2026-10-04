"""Cart API views."""

from __future__ import annotations

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.cart.serializers import CartItemSerializer, CartSerializer
from apps.cart.services import add_to_cart, get_or_create_cart, set_item_quantity
from apps.catalog.models import Product


class CartDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):  # noqa: ANN001
        cart = get_or_create_cart(request)
        return Response(CartSerializer(cart, context={"request": request}).data)


class CartItemCreateView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):  # noqa: ANN001
        serializer = CartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = Product.objects.get(
            pk=serializer.validated_data["product_id"],
            is_active=True,
        )
        cart = get_or_create_cart(request)
        item = add_to_cart(cart, product, serializer.validated_data.get("quantity", 1))
        return Response(
            CartItemSerializer(item, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class CartItemUpdateView(APIView):
    permission_classes = [permissions.AllowAny]

    def patch(self, request, product_id: int):  # noqa: ANN001
        quantity = int(request.data.get("quantity", 1))
        cart = get_or_create_cart(request)
        set_item_quantity(cart, product_id, quantity)
        return Response(CartSerializer(cart, context={"request": request}).data)

    def delete(self, request, product_id: int):  # noqa: ANN001
        cart = get_or_create_cart(request)
        set_item_quantity(cart, product_id, 0)
        return Response(status=status.HTTP_204_NO_CONTENT)
