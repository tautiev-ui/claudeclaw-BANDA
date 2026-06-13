from django.contrib import admin

from .models import IndexingMonitorURL, LaunchQACheck, WebmasterSetupTask


@admin.register(WebmasterSetupTask)
class WebmasterSetupTaskAdmin(admin.ModelAdmin):
    list_display = ("platform", "task_key", "title", "status", "updated_at")
    list_filter = ("platform", "status")
    search_fields = ("title", "task_key", "description", "notes")
    readonly_fields = ("created_at", "updated_at")


@admin.register(LaunchQACheck)
class LaunchQACheckAdmin(admin.ModelAdmin):
    list_display = ("category", "check_key", "title", "target", "status", "updated_at")
    list_filter = ("category", "status")
    search_fields = ("title", "check_key", "target", "expected", "evidence")
    readonly_fields = ("created_at", "updated_at")


@admin.register(IndexingMonitorURL)
class IndexingMonitorURLAdmin(admin.ModelAdmin):
    list_display = ("url", "page_type", "index_status", "http_status", "is_empty_profile", "last_checked_at", "updated_at")
    list_filter = ("index_status", "page_type", "is_empty_profile")
    search_fields = ("url", "page_type", "notes")
    readonly_fields = ("created_at", "updated_at")
