"""Storefront cart, checkout, and favourite actions."""

from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_POST

from apps.cart.services import add_to_cart, get_or_create_cart, set_item_quantity
from apps.catalog.models import Product
from apps.favourites.models import Favourite
from apps.orders.services import create_order_from_cart


def _wants_json(request) -> bool:  # noqa: ANN001
    accept = request.headers.get("Accept", "")
    return "application/json" in accept or request.headers.get("X-Requested-With") == "XMLHttpRequest"


def cart_detail(request):  # noqa: ANN001
    cart = get_or_create_cart(request)
    items = cart.items.select_related("product", "product__category").prefetch_related(
        "product__images"
    )
    return render(
        request,
        "store/cart.html",
        {"cart": cart, "items": items},
    )


@require_POST
def cart_add(request, product_id: int):  # noqa: ANN001
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    quantity = max(1, int(request.POST.get("quantity") or 1))
    cart = get_or_create_cart(request)
    add_to_cart(cart, product, quantity)
    if _wants_json(request):
        return JsonResponse(
            {
                "ok": True,
                "item_count": cart.item_count,
                "message": f"Added {product.name} to cart",
            }
        )
    messages.success(request, f"Added {product.name} to your cart.")
    next_url = request.POST.get("next") or reverse("store-cart")
    return redirect(next_url)


@require_http_methods(["POST"])
def cart_update(request, product_id: int):  # noqa: ANN001
    quantity = int(request.POST.get("quantity") or 0)
    cart = get_or_create_cart(request)
    set_item_quantity(cart, product_id, quantity)
    if _wants_json(request):
        return JsonResponse({"ok": True, "item_count": cart.item_count})
    return redirect("store-cart")


@require_POST
def cart_remove(request, product_id: int):  # noqa: ANN001
    cart = get_or_create_cart(request)
    set_item_quantity(cart, product_id, 0)
    if _wants_json(request):
        return JsonResponse({"ok": True, "item_count": cart.item_count})
    messages.info(request, "Item removed from cart.")
    return redirect("store-cart")


@require_http_methods(["GET", "POST"])
def checkout(request):  # noqa: ANN001
    cart = get_or_create_cart(request)
    items = cart.items.select_related("product").prefetch_related("product__images")
    if not items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect("store-cart")

    if request.method == "POST":
        email = (
            request.POST.get("email")
            or (request.user.email if request.user.is_authenticated else "")
        ).strip()
        address = (request.POST.get("shipping_address") or "").strip()
        notes = (request.POST.get("notes") or "").strip()
        if not email:
            messages.error(request, "Email is required for checkout.")
            return render(
                request,
                "store/checkout.html",
                {"cart": cart, "items": items},
            )
        try:
            order = create_order_from_cart(
                cart=cart,
                email=email,
                shipping_address=address,
                notes=notes,
                user=request.user if request.user.is_authenticated else None,
            )
        except ValueError as exc:
            messages.error(request, str(exc))
            return redirect("store-cart")
        messages.success(request, f"Order {order.number} placed.")
        if request.user.is_authenticated:
            return redirect("account-order-detail", number=order.number)
        return render(request, "store/checkout_done.html", {"order": order})

    return render(request, "store/checkout.html", {"cart": cart, "items": items})


@login_required
@require_POST
def favourite_toggle(request, product_id: int):  # noqa: ANN001
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    fav = Favourite.objects.filter(user=request.user, product=product).first()
    if fav:
        fav.delete()
        favourited = False
        message = f"Removed {product.name} from favourites"
    else:
        Favourite.objects.create(user=request.user, product=product)
        favourited = True
        message = f"Saved {product.name} to favourites"
    if _wants_json(request):
        return JsonResponse(
            {
                "ok": True,
                "favourited": favourited,
                "favourite_count": request.user.favourites.count(),
                "message": message,
            }
        )
    messages.success(request, message)
    next_url = request.POST.get("next") or reverse("account-favourites")
    return redirect(next_url)
