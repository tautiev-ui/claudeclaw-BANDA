from django.contrib import admin

from apps.search.models import SearchQuery


@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ("normalized_query", "result_count", "updated_at")
    search_fields = ("query", "normalized_query")
    readonly_fields = ("created_at", "updated_at")
