from django.contrib import admin

from .models import City, Country


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "slug", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "code", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "region", "slug", "is_active")
    list_filter = ("country", "is_active")
    search_fields = ("name", "region", "slug")
    prepopulated_fields = {"slug": ("name",)}
