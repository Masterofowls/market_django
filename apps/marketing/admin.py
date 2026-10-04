from django.contrib import admin

from apps.marketing.models import Banner, Slider, SliderImage


class SliderImageInline(admin.TabularInline):
    model = SliderImage
    extra = 1


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "sort_order", "starts_at", "ends_at")
    list_filter = ("is_active",)
    search_fields = ("title", "subtitle")


@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [SliderImageInline]
