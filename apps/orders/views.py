"""Order API views."""

from __future__ import annotations

from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.cart.services import get_or_create_cart
from apps.orders.models import Order
from apps.orders.serializers import CheckoutSerializer, OrderSerializer
from apps.orders.services import create_order_from_cart


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "number"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items")


class CheckoutView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):  # noqa: ANN001
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart = get_or_create_cart(request)
        email = serializer.validated_data.get("email") or getattr(request.user, "email", "")
        if not email:
            return Response(
                {"detail": "email is required for guest checkout"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            order = create_order_from_cart(
                cart=cart,
                email=email,
                shipping_address=serializer.validated_data.get("shipping_address", ""),
                notes=serializer.validated_data.get("notes", ""),
                user=request.user if request.user.is_authenticated else None,
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
