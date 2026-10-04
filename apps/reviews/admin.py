from django.contrib import admin

from apps.reviews.models import Comment, Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "is_approved", "created_at")
    list_filter = ("rating", "is_approved")
    search_fields = ("product__name", "user__username", "title", "body")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "parent", "is_approved", "created_at")
    list_filter = ("is_approved",)
    search_fields = ("product__name", "user__username", "body")
