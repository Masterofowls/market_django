import pytest
from apps.catalog.models import Product
from apps.orders.models import Order
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_cart_and_checkout_flow():
    product = Product.objects.create(
        name="USB Hub",
        sku="SKU-HUB-1",
        price="39.00",
        discount_percent="0",
        stock=10,
    )
    client = APIClient()

    add = client.post(
        reverse("cart-item-create"),
        {"product_id": product.id, "quantity": 2},
        format="json",
    )
    assert add.status_code == 201

    cart = client.get(reverse("cart-detail"))
    assert cart.status_code == 200
    assert cart.data["item_count"] == 2

    checkout = client.post(
        reverse("checkout"),
        {"email": "guest@example.com", "shipping_address": "1 Test Way"},
        format="json",
    )
    assert checkout.status_code == 201
    assert Order.objects.filter(email="guest@example.com").exists()
