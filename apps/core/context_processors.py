"""Storefront template context."""

from __future__ import annotations

from apps.cart.services import get_or_create_cart
from apps.catalog.models import Category
from apps.favourites.models import Favourite


def storefront(request):  # noqa: ANN001
    cart_count = 0
    favourite_ids: set[int] = set()
    favourite_count = 0
    header_categories = []
    try:
        header_categories = list(
            Category.objects.filter(is_active=True, show_in_header=True).order_by(
                "header_order",
                "name",
            )
        )
        if hasattr(request, "session"):
            cart = get_or_create_cart(request)
            cart_count = cart.item_count
        if getattr(request, "user", None) and request.user.is_authenticated:
            favourite_ids = set(
                Favourite.objects.filter(user=request.user).values_list(
                    "product_id", flat=True
                )
            )
            favourite_count = len(favourite_ids)
    except Exception:  # noqa: BLE001
        # Avoid breaking pages during migrate / early boot.
        pass

    return {
        "STORE_NAME": "ElectroMarket",
        "STORE_TAGLINE": "Flagship smartphones from Samsung, Nothing, and Apple",
        "cart_count": cart_count,
        "favourite_ids": favourite_ids,
        "favourite_count": favourite_count,
        "header_categories": header_categories,
    }
