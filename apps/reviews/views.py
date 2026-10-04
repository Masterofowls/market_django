"""Reviews and commentaries API."""

from __future__ import annotations

from rest_framework import permissions, viewsets

from apps.reviews.models import Comment, Review
from apps.reviews.serializers import CommentSerializer, ReviewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ["product", "rating"]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        return Review.objects.filter(is_approved=True).select_related("user", "product")

    def perform_create(self, serializer):  # noqa: ANN001
        serializer.save(user=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ["product", "parent"]
    http_method_names = ["get", "post", "delete", "head", "options"]

    def get_queryset(self):
        return Comment.objects.filter(is_approved=True).select_related("user", "product")

    def perform_create(self, serializer):  # noqa: ANN001
        serializer.save(user=self.request.user)
