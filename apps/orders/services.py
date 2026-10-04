"""Checkout: cart → order."""

from __future__ import annotations

from decimal import Decimal

from django.db import transaction

from apps.cart.models import Cart
from apps.notifications.models import Notification
from apps.orders.models import Order, OrderItem


@transaction.atomic
def create_order_from_cart(
    *,
    cart: Cart,
    email: str,
    shipping_address: str = "",
    notes: str = "",
    user=None,  # noqa: ANN001
) -> Order:
    if not cart.items.exists():
        raise ValueError("Cart is empty")

    order = Order.objects.create(
        user=user or cart.user,
        email=email,
        shipping_address=shipping_address,
        notes=notes,
        status=Order.Status.PENDING,
    )
    discount_total = Decimal("0.00")
    for item in cart.items.select_related("product"):
        OrderItem.objects.create(
            order=order,
            product=item.product,
            product_name=item.product.name,
            product_sku=item.product.sku,
            quantity=item.quantity,
            unit_price=item.unit_price,
            line_total=item.line_total,
        )
        list_line = item.product.price * item.quantity
        discount_total += list_line - item.line_total

    order.discount_total = discount_total.quantize(Decimal("0.01"))
    order.recalculate()
    cart.items.all().delete()

    if order.user_id:
        Notification.objects.create(
            user=order.user,
            kind=Notification.Kind.ORDER,
            title=f"Order {order.number} placed",
            body=f"Your order total is {order.grand_total}.",
            link_url=f"/account/orders/{order.number}/",
        )
    return order
