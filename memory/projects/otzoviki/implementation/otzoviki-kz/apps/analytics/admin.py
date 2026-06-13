from django.contrib import admin

from apps.analytics.models import AnalyticsEvent


@admin.register(AnalyticsEvent)
class AnalyticsEventAdmin(admin.ModelAdmin):
    list_display = ("event_type", "path", "query", "company", "created_at")
    list_filter = ("event_type", "created_at")
    search_fields = ("path", "query", "company__name")
    readonly_fields = ("event_type", "path", "query", "company", "metadata", "created_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
