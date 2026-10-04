"""Cart helpers for session/user carts."""

from __future__ import annotations

from django.db import transaction

from apps.cart.models import Cart, CartItem
from apps.catalog.models import Product


def get_or_create_cart(request) -> Cart:  # noqa: ANN001
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return cart

    if not request.session.session_key:
        request.session.create()
    cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key, user=None)
    return cart


@transaction.atomic
def add_to_cart(cart: Cart, product: Product, quantity: int = 1) -> CartItem:
    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={"quantity": quantity, "unit_price": product.final_price},
    )
    if not created:
        item.quantity += quantity
        item.unit_price = product.final_price
        item.save(update_fields=["quantity", "unit_price"])
    return item


def set_item_quantity(cart: Cart, product_id: int, quantity: int) -> None:
    if quantity <= 0:
        CartItem.objects.filter(cart=cart, product_id=product_id).delete()
        return
    CartItem.objects.filter(cart=cart, product_id=product_id).update(quantity=quantity)
