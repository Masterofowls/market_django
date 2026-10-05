from django.urls import include, path

from apps.core import commerce_views, views
from apps.reviews import storefront as review_views

urlpatterns = [
    path("", views.HomeView.as_view(), name="store-home"),
    path("store/", views.HomeView.as_view(), name="store-home-alias"),
    path("products/", views.ProductListView.as_view(), name="store-product-list"),
    path(
        "products/<slug:slug>/",
        views.ProductDetailView.as_view(),
        name="store-product-detail",
    ),
    path(
        "products/<slug:slug>/share/",
        views.product_share,
        name="store-product-share",
    ),
    path(
        "products/<slug:slug>/review/",
        review_views.product_review,
        name="store-product-review",
    ),
    path(
        "products/<slug:slug>/comment/",
        review_views.product_comment,
        name="store-product-comment",
    ),
    path("categories/", views.category_list, name="store-category-list"),
    path("categories/<slug:slug>/", views.category_detail, name="store-category-detail"),
    path("cart/", commerce_views.cart_detail, name="store-cart"),
    path("cart/add/<int:product_id>/", commerce_views.cart_add, name="store-cart-add"),
    path(
        "cart/update/<int:product_id>/",
        commerce_views.cart_update,
        name="store-cart-update",
    ),
    path(
        "cart/remove/<int:product_id>/",
        commerce_views.cart_remove,
        name="store-cart-remove",
    ),
    path("checkout/", commerce_views.checkout, name="store-checkout"),
    path(
        "favourites/toggle/<int:product_id>/",
        commerce_views.favourite_toggle,
        name="store-favourite-toggle",
    ),
    path("account/", include("apps.accounts.urls")),
]
