from django.contrib import admin

from .models import Author, EditorialPolicy, MethodologyVersion


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("full_name", "role", "is_active", "updated_at")
    list_filter = ("role", "is_active")
    search_fields = ("full_name", "bio", "expertise")
    prepopulated_fields = {"slug": ("full_name",)}


@admin.register(MethodologyVersion)
class MethodologyVersionAdmin(admin.ModelAdmin):
    list_display = ("version", "title", "is_current", "published_at", "updated_at")
    list_filter = ("is_current",)
    search_fields = ("version", "title", "summary", "body")


@admin.register(EditorialPolicy)
class EditorialPolicyAdmin(admin.ModelAdmin):
    list_display = ("title", "kind", "is_published", "updated_at")
    list_filter = ("kind", "is_published")
    search_fields = ("title", "summary", "body")
    prepopulated_fields = {"slug": ("title",)}
