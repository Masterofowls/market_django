"""Favourites API."""

from __future__ import annotations

from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from apps.catalog.models import Product
from apps.favourites.models import Favourite
from apps.favourites.serializers import FavouriteSerializer


class FavouriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavouriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "delete", "head", "options"]

    def get_queryset(self):
        return (
            Favourite.objects.filter(user=self.request.user)
            .select_related(
                "product",
                "product__category",
            )
            .prefetch_related("product__tags", "product__images")
        )

    def create(self, request, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003
        product = Product.objects.get(pk=request.data.get("product_id"), is_active=True)
        fav, created = Favourite.objects.get_or_create(user=request.user, product=product)
        serializer = self.get_serializer(fav)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
