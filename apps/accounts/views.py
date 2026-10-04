"""Signed-in account hub: profile, security, orders, favourites, history."""

from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from allauth.mfa.models import Authenticator

from apps.accounts.forms import ProfileForm
from apps.catalog.history import viewed_products_for
from apps.favourites.models import Favourite
from apps.orders.models import Order


@login_required
def account_home(request):  # noqa: ANN001
    orders = Order.objects.filter(user=request.user).prefetch_related("items")[:5]
    favourites = (
        Favourite.objects.filter(user=request.user)
        .select_related("product", "product__category")
        .prefetch_related("product__images")[:6]
    )
    history = viewed_products_for(request, limit=6)
    passkeys = Authenticator.objects.filter(
        user=request.user,
        type=Authenticator.Type.WEBAUTHN,
    ).count()
    return render(
        request,
        "account/home.html",
        {
            "orders": orders,
            "favourites": favourites,
            "history": history,
            "passkey_count": passkeys,
            "order_count": Order.objects.filter(user=request.user).count(),
            "favourite_count": Favourite.objects.filter(user=request.user).count(),
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def account_profile(request):  # noqa: ANN001
    form = ProfileForm(request.POST or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profile updated.")
        return redirect("account-profile")
    return render(request, "account/profile.html", {"form": form})


@login_required
def account_security(request):  # noqa: ANN001
    authenticators = Authenticator.objects.filter(user=request.user).order_by("type", "created_at")
    return render(
        request,
        "account/security.html",
        {
            "authenticators": authenticators,
            "has_totp": authenticators.filter(type=Authenticator.Type.TOTP).exists(),
            "has_webauthn": authenticators.filter(type=Authenticator.Type.WEBAUTHN).exists(),
            "has_recovery": authenticators.filter(
                type=Authenticator.Type.RECOVERY_CODES
            ).exists(),
        },
    )


@login_required
def account_orders(request):  # noqa: ANN001
    orders = Order.objects.filter(user=request.user).prefetch_related("items")
    return render(request, "account/orders.html", {"orders": orders})


@login_required
def account_order_detail(request, number: str):  # noqa: ANN001
    order = get_object_or_404(
        Order.objects.prefetch_related("items", "items__product"),
        user=request.user,
        number=number,
    )
    return render(request, "account/order_detail.html", {"order": order})


@login_required
def account_favourites(request):  # noqa: ANN001
    favourites = (
        Favourite.objects.filter(user=request.user)
        .select_related("product", "product__category")
        .prefetch_related("product__images", "product__tags")
    )
    return render(request, "account/favourites.html", {"favourites": favourites})


@login_required
def account_history(request):  # noqa: ANN001
    history = viewed_products_for(request, limit=48)
    return render(request, "account/history.html", {"history": history})
