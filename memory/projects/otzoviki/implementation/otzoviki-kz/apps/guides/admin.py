from django.contrib import admin

from apps.guides.models import (
    Guide,
    GuideCategory,
    GuideChecklistItem,
    GuideFAQ,
    GuideInternalLink,
    GuideRiskItem,
    GuideSourceReference,
)


class GuideChecklistItemInline(admin.TabularInline):
    model = GuideChecklistItem
    extra = 0


class GuideRiskItemInline(admin.TabularInline):
    model = GuideRiskItem
    extra = 0


class GuideFAQInline(admin.TabularInline):
    model = GuideFAQ
    extra = 0


class GuideSourceReferenceInline(admin.TabularInline):
    model = GuideSourceReference
    extra = 0


class GuideInternalLinkInline(admin.TabularInline):
    model = GuideInternalLink
    extra = 0


@admin.register(GuideCategory)
class GuideCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "position", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Guide)
class GuideAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "status", "launch_ready", "quality_issue_count", "published_at", "last_verified_at")
    list_filter = ("status", "category")
    search_fields = ("title", "slug", "summary", "body")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [
        GuideChecklistItemInline,
        GuideRiskItemInline,
        GuideFAQInline,
        GuideSourceReferenceInline,
        GuideInternalLinkInline,
    ]

    @admin.display(boolean=True, description="Launch ready")
    def launch_ready(self, obj):
        return obj.is_launch_ready

    @admin.display(description="Quality issues")
    def quality_issue_count(self, obj):
        return len(obj.quality_issues)
