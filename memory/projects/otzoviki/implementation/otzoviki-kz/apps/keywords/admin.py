from django.contrib import admin

from apps.keywords.models import Keyword, KeywordCluster, KeywordPageMap, KeywordURLCompetitorEvidence


@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):
    list_display = ("normalized_query", "frequency", "source", "region", "target_cluster", "updated_at")
    list_filter = ("source", "region", "target_cluster")
    search_fields = ("query", "normalized_query", "target_cluster")


@admin.register(KeywordURLCompetitorEvidence)
class KeywordURLCompetitorEvidenceAdmin(admin.ModelAdmin):
    list_display = ("keyword", "domain", "position", "collected_at")
    list_filter = ("domain",)
    search_fields = ("keyword__normalized_query", "url", "domain", "title", "h1")


class KeywordPageMapInline(admin.TabularInline):
    model = KeywordPageMap
    extra = 0


@admin.register(KeywordCluster)
class KeywordClusterAdmin(admin.ModelAdmin):
    list_display = ("slug", "name", "intent", "page_type", "updated_at")
    list_filter = ("intent", "page_type")
    search_fields = ("slug", "name")
    inlines = [KeywordPageMapInline]


@admin.register(KeywordPageMap)
class KeywordPageMapAdmin(admin.ModelAdmin):
    list_display = ("cluster", "page_type", "canonical_pattern", "priority", "is_indexable_candidate")
    list_filter = ("page_type", "priority", "is_indexable_candidate")
    search_fields = ("cluster__slug", "canonical_pattern", "notes")
