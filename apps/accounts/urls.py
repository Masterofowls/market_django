"""Account hub URLs."""

from django.urls import path

from apps.accounts import views

urlpatterns = [
    path("", views.account_home, name="account-home"),
    path("profile/", views.account_profile, name="account-profile"),
    path("security/", views.account_security, name="account-security"),
    path("orders/", views.account_orders, name="account-orders"),
    path("orders/<str:number>/", views.account_order_detail, name="account-order-detail"),
    path("favourites/", views.account_favourites, name="account-favourites"),
    path("history/", views.account_history, name="account-history"),
]
