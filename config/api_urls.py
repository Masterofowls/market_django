"""DRF router URLconf."""

from __future__ import annotations

from apps.cart.views import CartDetailView, CartItemCreateView, CartItemUpdateView
from apps.catalog.views import (
    CatalogSectionViewSet,
    CategoryViewSet,
    ProductViewSet,
    TagViewSet,
)
from apps.favourites.views import FavouriteViewSet
from apps.marketing.views import BannerViewSet, SliderViewSet
from apps.notifications.views import NotificationViewSet
from apps.orders.views import CheckoutView, OrderViewSet
from apps.recommendations.views import PersonalizedRecommendationView, SuggestionView
from apps.reviews.views import CommentViewSet, ReviewViewSet
from django.urls import include, path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="category")
router.register("tags", TagViewSet, basename="tag")
router.register("products", ProductViewSet, basename="product")
router.register("sections", CatalogSectionViewSet, basename="section")
router.register("favourites", FavouriteViewSet, basename="favourite")
router.register("reviews", ReviewViewSet, basename="review")
router.register("comments", CommentViewSet, basename="comment")
router.register("banners", BannerViewSet, basename="banner")
router.register("sliders", SliderViewSet, basename="slider")
router.register("notifications", NotificationViewSet, basename="notification")
router.register("orders", OrderViewSet, basename="order")

urlpatterns = [
    path("", include(router.urls)),
    path("cart/", CartDetailView.as_view(), name="cart-detail"),
    path("cart/items/", CartItemCreateView.as_view(), name="cart-item-create"),
    path(
        "cart/items/<int:product_id>/",
        CartItemUpdateView.as_view(),
        name="cart-item-update",
    ),
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("suggestions/", SuggestionView.as_view(), name="suggestions"),
    path(
        "recommendations/me/",
        PersonalizedRecommendationView.as_view(),
        name="recommendations-me",
    ),
]
