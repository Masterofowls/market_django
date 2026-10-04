"""Django Ninja API surface (lightweight store endpoints)."""

from __future__ import annotations

from apps.catalog.models import Category, Product, Tag
from apps.recommendations.services import suggest_products
from ninja import NinjaAPI, Schema
from ninja.security import django_auth

api = NinjaAPI(
    title="ElectroMarket Ninja",
    version="1.0.0",
    urls_namespace="ninja",
)


class ProductOut(Schema):
    id: int
    name: str
    slug: str
    sku: str
    price: float
    discount_percent: float
    final_price: float
    category_id: int | None
    average_rating: float
    is_featured: bool


class CategoryOut(Schema):
    id: int
    name: str
    slug: str


class TagOut(Schema):
    id: int
    name: str
    slug: str


class HealthOut(Schema):
    status: str
    service: str


@api.get("/health", response=HealthOut, auth=None)
def health(request):  # noqa: ANN001, ARG001
    return {"status": "ok", "service": "electromarket"}


@api.get("/products", response=list[ProductOut], auth=None)
def list_products(
    request,  # noqa: ANN001, ARG001
    q: str = "",
    category_id: int | None = None,
    tag: str = "",
    limit: int = 24,
):
    qs = suggest_products(query=q, category_id=category_id, tag=tag, limit=min(limit, 100))
    return [
        ProductOut(
            id=p.id,
            name=p.name,
            slug=p.slug,
            sku=p.sku,
            price=float(p.price),
            discount_percent=float(p.discount_percent),
            final_price=float(p.final_price),
            category_id=p.category_id,
            average_rating=float(p.average_rating),
            is_featured=p.is_featured,
        )
        for p in qs
    ]


@api.get("/products/{slug}", response=ProductOut, auth=None)
def product_detail(request, slug: str):  # noqa: ANN001, ARG001
    p = Product.objects.get(slug=slug, is_active=True)
    return ProductOut(
        id=p.id,
        name=p.name,
        slug=p.slug,
        sku=p.sku,
        price=float(p.price),
        discount_percent=float(p.discount_percent),
        final_price=float(p.final_price),
        category_id=p.category_id,
        average_rating=float(p.average_rating),
        is_featured=p.is_featured,
    )


@api.get("/categories", response=list[CategoryOut], auth=None)
def list_categories(request):  # noqa: ANN001, ARG001
    return list(Category.objects.filter(is_active=True).values("id", "name", "slug"))


@api.get("/tags", response=list[TagOut], auth=None)
def list_tags(request):  # noqa: ANN001, ARG001
    return list(Tag.objects.all().values("id", "name", "slug"))


@api.get("/me/ping", auth=django_auth)
def me_ping(request):  # noqa: ANN001
    return {"ok": True, "user": request.user.get_username()}
