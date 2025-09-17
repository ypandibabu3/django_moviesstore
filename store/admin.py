from django.contrib import admin
from .models import Movie, Review, Order, OrderItem
from django.utils.html import format_html

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "created_at", "image_preview")
    search_fields = ("title",)
    readonly_fields = ("image_preview",)
    fields = ("title", "price", "description", "image", "image_url", "image_preview")

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:80px;" />', obj.image.url)
        if obj.image_url:
            return format_html('<img src="{}" style="max-height:80px;" />', obj.image_url)
        return "-"

    image_preview.short_description = "Image"

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("movie", "user", "rating", "created_at")
    list_filter = ("rating",)
    search_fields = ("movie__title", "user__username")

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at")
    inlines = [OrderItemInline]