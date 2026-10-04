"""Review/comment serializers."""

from __future__ import annotations

from rest_framework import serializers

from apps.reviews.models import Comment, Review


class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Review
        fields = (
            "id",
            "product",
            "username",
            "rating",
            "title",
            "body",
            "created_at",
        )
        read_only_fields = ("created_at",)


class CommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Comment
        fields = (
            "id",
            "product",
            "username",
            "parent",
            "body",
            "created_at",
        )
        read_only_fields = ("created_at",)
