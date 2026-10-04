from __future__ import annotations

from rest_framework import serializers

from apps.notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = (
            "id",
            "kind",
            "title",
            "body",
            "link_url",
            "is_read",
            "created_at",
        )
        read_only_fields = ("kind", "title", "body", "link_url", "created_at")
