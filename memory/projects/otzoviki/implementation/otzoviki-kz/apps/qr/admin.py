from django.contrib import admin

from apps.qr.models import QRReviewFlow, QRScanEvent, ReviewPlatformLink


class ReviewPlatformLinkInline(admin.TabularInline):
    model = ReviewPlatformLink
    extra = 0


@admin.register(QRReviewFlow)
class QRReviewFlowAdmin(admin.ModelAdmin):
    list_display = ("company", "label", "token", "is_active", "scan_count", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("company__name", "label", "token")
    readonly_fields = ("token", "sentiment_filter_enabled", "scan_count", "created_at", "updated_at")
    inlines = [ReviewPlatformLinkInline]


@admin.register(ReviewPlatformLink)
class ReviewPlatformLinkAdmin(admin.ModelAdmin):
    list_display = ("flow", "platform", "capability", "is_active", "click_count", "last_checked_at")
    list_filter = ("platform", "capability", "is_active")
    search_fields = ("flow__company__name", "url")


@admin.register(QRScanEvent)
class QRScanEventAdmin(admin.ModelAdmin):
    list_display = ("flow", "user_agent_family", "created_at")
    search_fields = ("flow__company__name", "user_agent_family")
    readonly_fields = ("created_at",)
