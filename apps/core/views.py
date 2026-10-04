"""Storefront views for the electronics marketplace."""

from __future__ import annotations

from django.db.models import F, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView, TemplateView

from apps.catalog.history import record_product_view
from apps.catalog.models import Category, Product, ProductShare
from apps.marketing.models import Banner, Slider
from apps.recommendations.services import recommend_for_product


def _parse_specs(description: str) -> list[tuple[str, str]]:
    specs: list[tuple[str, str]] = []
    for line in description.splitlines():
        text = line.strip().lstrip("•").strip()
        if ": " not in text:
            continue
        key, value = text.split(": ", 1)
        skip = key.startswith("Images sourced") or key == "Key specifications"
        if skip:
            continue
        if key and value and len(key) < 40:
            specs.append((key, value))
    return specs


class HomeView(TemplateView):
    template_name = "store/home.html"

    def get_context_data(self, **kwargs):  # noqa: ANN003
        ctx = super().get_context_data(**kwargs)
        featured = list(
            Product.objects.filter(is_active=True, is_featured=True)
            .select_related("category")
            .prefetch_related("images", "tags")[:8]
        )
        hero = featured[0] if featured else (
            Product.objects.filter(is_active=True).prefetch_related("images").first()
        )
        hero_image = None
        if hero:
            image = hero.images.filter(is_primary=True).first() or hero.images.first()
            if image:
                try:
                    hero_image = image.preview.url
                except Exception:  # noqa: BLE001
                    hero_image = image.image.url

        ctx["banners"] = Banner.objects.filter(is_active=True)[:5]
        ctx["hero_slider"] = Slider.objects.filter(slug="home", is_active=True).first()
        ctx["featured"] = featured
        ctx["brands"] = Category.objects.filter(
            is_active=True,
            parent__slug="smartphones",
        ).order_by("name")
        ctx["categories"] = Category.objects.filter(is_active=True, parent=None)[:12]
        ctx["hero_image"] = hero_image
        ctx["hero_product"] = hero
        return ctx


class ProductListView(ListView):
    model = Product
    template_name = "store/product_list.html"
    context_object_name = "products"
    paginate_by = 24

    def get_queryset(self):
        qs = (
            Product.objects.filter(is_active=True)
            .select_related("category")
            .prefetch_related("tags", "images")
        )
        q = (self.request.GET.get("q") or "").strip()
        category = self.request.GET.get("category")
        tag = self.request.GET.get("tag")
        if q:
            filters = (
                Q(name__icontains=q)
                | Q(sku__icontains=q)
                | Q(slug__icontains=q)
                | Q(short_description__icontains=q)
            )
            if q.isdigit():
                filters |= Q(pk=int(q))
            qs = qs.filter(filters)
        if category:
            qs = qs.filter(category__slug=category) | qs.filter(category__parent__slug=category)
        if tag:
            qs = qs.filter(tags__slug=tag)
        return qs.distinct()

    def get_context_data(self, **kwargs):  # noqa: ANN003
        ctx = super().get_context_data(**kwargs)
        ctx["filter_categories"] = Category.objects.filter(is_active=True).order_by("name")
        return ctx


@method_decorator(ensure_csrf_cookie, name="dispatch")
class ProductDetailView(DetailView):
    model = Product
    template_name = "store/product_detail.html"
    context_object_name = "product"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Product.objects.filter(is_active=True).prefetch_related(
            "images",
            "tags",
            "reviews",
            "comments",
        )

    def get(self, request, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003
        response = super().get(request, *args, **kwargs)
        record_product_view(request, self.object)
        return response

    def get_context_data(self, **kwargs):  # noqa: ANN003
        ctx = super().get_context_data(**kwargs)
        product = self.object
        public_path = reverse("store-product-detail", kwargs={"slug": product.slug})
        ctx["specs"] = _parse_specs(product.description)
        ctx["public_id"] = product.pk
        ctx["public_url"] = self.request.build_absolute_uri(public_path)
        ctx["similar_products"] = list(recommend_for_product(product, limit=4))
        ctx["is_favourited"] = (
            request_user_has_favourite(self.request, product.pk)
            if self.request.user.is_authenticated
            else False
        )
        return ctx


def request_user_has_favourite(request, product_id: int) -> bool:  # noqa: ANN001
    from apps.favourites.models import Favourite

    return Favourite.objects.filter(user=request.user, product_id=product_id).exists()


@require_POST
def product_share(request, slug: str):  # noqa: ANN001
    product = get_object_or_404(Product, slug=slug, is_active=True)
    channel = (request.POST.get("channel") or request.GET.get("channel") or "link").strip()
    ProductShare.objects.create(
        product=product,
        channel=channel[:64],
        shared_by=request.user if request.user.is_authenticated else None,
    )
    Product.objects.filter(pk=product.pk).update(share_count=F("share_count") + 1)
    product.refresh_from_db(fields=["share_count"])
    public_url = request.build_absolute_uri(
        reverse("store-product-detail", kwargs={"slug": product.slug})
    )
    return JsonResponse(
        {
            "ok": True,
            "public_url": public_url,
            "public_id": product.pk,
            "share_count": product.share_count,
        }
    )


def category_list(request):  # noqa: ANN001
    categories = Category.objects.filter(is_active=True)
    return render(request, "store/category_list.html", {"categories": categories})


def category_detail(request, slug: str):  # noqa: ANN001
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = (
        category.products.filter(is_active=True)
        .select_related("category")
        .prefetch_related("images", "tags")
    )
    if not products.exists() and category.children.exists():
        products = (
            Product.objects.filter(is_active=True, category__parent=category)
            .select_related("category")
            .prefetch_related("images", "tags")
        )
    return render(
        request,
        "store/category_detail.html",
        {"category": category, "products": products},
    )
