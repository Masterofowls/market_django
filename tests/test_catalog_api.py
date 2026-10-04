import pytest
from apps.catalog.models import Category, Product, Tag
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_product_search_by_name_category_tag():
    category = Category.objects.create(name="Audio", slug="audio")
    tag = Tag.objects.create(name="Wireless", slug="wireless")
    product = Product.objects.create(
        name="Noise Cancelling Buds",
        sku="SKU-BUDS-1",
        category=category,
        price="149.00",
        stock=5,
    )
    product.tags.add(tag)

    client = APIClient()
    url = reverse("product-list")

    by_name = client.get(url, {"search": "Cancelling"})
    assert by_name.status_code == 200
    assert by_name.data["count"] == 1

    by_category = client.get(url, {"category": category.id})
    assert by_category.data["count"] == 1

    by_tag = client.get(url, {"tag": "wireless"})
    assert by_tag.data["count"] == 1


@pytest.mark.django_db
def test_share_increments_counter():
    product = Product.objects.create(name="Speaker", sku="SKU-SPK-1", price="99.00")
    client = APIClient()
    url = reverse("product-share", kwargs={"slug": product.slug})
    response = client.post(url, {"channel": "copy"}, format="json")
    assert response.status_code == 201
    product.refresh_from_db()
    assert product.share_count == 1
