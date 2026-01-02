from django.contrib import admin

from .models import Category, Fact


@admin.register(Fact)
class FactAdmin(admin.ModelAdmin):
    list_display = ("fact", "identifier", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("fact", "identifier", "description")
    list_display_links = ("fact", "identifier")
    prepopulated_fields = {"identifier": ("fact",)}


admin.site.register(Category)
