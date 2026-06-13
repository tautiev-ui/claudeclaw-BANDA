from django.contrib import admin

from apps.evidence.models import Evidence

from .models import RatingSnapshot, Review, ReviewModerationLog


class ReviewModerationLogInline(admin.TabularInline):
    model = ReviewModerationLog
    extra = 0
    readonly_fields = ("moderator", "action", "from_status", "to_status", "note", "created_at")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


class ReviewPrivateProofEvidenceInline(admin.TabularInline):
    model = Evidence
    fk_name = "review"
    extra = 0
    readonly_fields = ("evidence_type", "title", "claim", "visibility", "captured_at", "created_at")
    fields = readonly_fields
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).filter(evidence_type=Evidence.EvidenceType.PRIVATE_PROOF)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("company", "title", "author_name", "status", "average_rating", "published_at")
    list_filter = ("status", "quality_rating", "timeline_rating", "price_rating", "communication_rating", "warranty_rating", "overall_rating")
    search_fields = ("company__name", "author_name", "title", "body")
    autocomplete_fields = ("company",)
    actions = ("mark_published", "mark_rejected", "mark_disputed")
    inlines = (ReviewModerationLogInline, ReviewPrivateProofEvidenceInline)

    def _moderate(self, request, queryset, *, status: str, action: str, note: str = ""):
        for review in queryset:
            from_status = review.status
            review.status = status
            if status == Review.Status.APPROVED:
                review.save()
            else:
                review.published_at = None
                review.save(update_fields=["status", "published_at", "updated_at"])
            moderator = getattr(request, "user", None)
            ReviewModerationLog.objects.create(
                review=review,
                moderator=moderator if moderator is not None and moderator.is_authenticated else None,
                action=action,
                from_status=from_status,
                to_status=status,
                note=note,
            )
            RatingSnapshot.objects.rebuild_for_company(review.company)

    @admin.action(description="Publish selected reviews")
    def mark_published(self, request, queryset):
        self._moderate(request, queryset, status=Review.Status.APPROVED, action=ReviewModerationLog.Action.PUBLISHED)

    @admin.action(description="Reject selected reviews")
    def mark_rejected(self, request, queryset):
        self._moderate(request, queryset, status=Review.Status.REJECTED, action=ReviewModerationLog.Action.REJECTED)

    @admin.action(description="Mark selected reviews as disputed")
    def mark_disputed(self, request, queryset):
        self._moderate(request, queryset, status=Review.Status.DISPUTED, action=ReviewModerationLog.Action.DISPUTED)


@admin.register(ReviewModerationLog)
class ReviewModerationLogAdmin(admin.ModelAdmin):
    list_display = ("review", "action", "from_status", "to_status", "moderator", "created_at")
    list_filter = ("action", "from_status", "to_status", "created_at")
    search_fields = ("review__company__name", "review__title", "moderator__username", "note")
    readonly_fields = ("review", "moderator", "action", "from_status", "to_status", "note", "created_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(RatingSnapshot)
class RatingSnapshotAdmin(admin.ModelAdmin):
    list_display = ("company", "average_rating", "review_count", "updated_at")
    search_fields = ("company__name",)
    readonly_fields = ("updated_at",)
