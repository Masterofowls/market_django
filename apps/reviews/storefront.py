"""Storefront review / feedback views."""

from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST

from apps.catalog.models import Product
from apps.reviews.forms import CommentForm, ReviewForm
from apps.reviews.models import Review


@login_required
@require_POST
def product_review(request, slug: str):  # noqa: ANN001
    product = get_object_or_404(Product, slug=slug, is_active=True)
    existing = Review.objects.filter(user=request.user, product=product).first()
    form = ReviewForm(request.POST, instance=existing)
    if form.is_valid():
        review = form.save(commit=False)
        review.user = request.user
        review.product = product
        review.is_approved = True
        review.save()
        messages.success(
            request,
            "Thanks — your rating and feedback were saved."
            if existing
            else "Thanks — your review was posted.",
        )
    else:
        messages.error(request, "Could not save your review. Check the rating and try again.")
    return redirect(
        reverse("store-product-detail", kwargs={"slug": product.slug}) + "#reviews"
    )


@login_required
@require_POST
def product_comment(request, slug: str):  # noqa: ANN001
    product = get_object_or_404(Product, slug=slug, is_active=True)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.user = request.user
        comment.product = product
        comment.is_approved = True
        comment.save()
        messages.success(request, "Comment posted.")
    else:
        messages.error(request, "Could not post your comment.")
    return redirect(
        reverse("store-product-detail", kwargs={"slug": product.slug}) + "#reviews"
    )
