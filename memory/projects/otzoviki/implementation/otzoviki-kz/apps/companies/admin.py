from django.contrib import admin

from apps.seo.admin_helpers import freshness_badge, indexability_badge

from .models import Company, CompanyService


class CompanyServiceInline(admin.TabularInline):
    model = CompanyService
    extra = 0
    autocomplete_fields = ("city", "service")


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "profile_status", "index_status", "indexability", "freshness", "source_count", "last_verified_at", "is_active")
    list_filter = ("profile_status", "index_status", "is_active")
    search_fields = ("name", "slug", "short_description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [CompanyServiceInline]

    @admin.display(description="Indexability")
    def indexability(self, obj):
        return indexability_badge(obj)

    @admin.display(description="Freshness")
    def freshness(self, obj):
        return freshness_badge(obj)


@admin.register(CompanyService)
class CompanyServiceAdmin(admin.ModelAdmin):
    list_display = ("company", "service", "city", "is_primary")
    list_filter = ("city", "service", "is_primary")
    search_fields = ("company__name", "service__name", "city__name")
    autocomplete_fields = ("company", "city", "service")
