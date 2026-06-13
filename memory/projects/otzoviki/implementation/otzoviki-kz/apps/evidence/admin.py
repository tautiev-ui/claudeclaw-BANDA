from django.contrib import admin

from .models import Evidence, EvidenceVisibilityLog, ExternalSource


@admin.register(ExternalSource)
class ExternalSourceAdmin(admin.ModelAdmin):
    list_display = ("company", "source_type", "name", "same_as_verified", "captured_at")
    list_filter = ("source_type", "same_as_verified")
    search_fields = ("company__name", "name", "url")
    autocomplete_fields = ("company",)


class EvidenceVisibilityLogInline(admin.TabularInline):
    model = EvidenceVisibilityLog
    extra = 0
    readonly_fields = ("moderator", "action", "from_visibility", "to_visibility", "note", "created_at")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Evidence)
class EvidenceAdmin(admin.ModelAdmin):
    list_display = ("company", "evidence_type", "title", "visibility", "captured_at")
    list_filter = ("evidence_type", "visibility")
    search_fields = ("company__name", "title", "claim", "source_url")
    autocomplete_fields = ("company", "external_source")
    actions = ("mark_public", "mark_private", "mark_admin_only")
    inlines = (EvidenceVisibilityLogInline,)

    def _set_visibility(self, request, queryset, *, visibility: str, action: str, note: str = ""):
        for evidence in queryset:
            if visibility == Evidence.Visibility.PUBLIC and evidence.evidence_type == Evidence.EvidenceType.PRIVATE_PROOF:
                continue
            from_visibility = evidence.visibility
            evidence.visibility = visibility
            evidence.save(update_fields=["visibility"])
            moderator = getattr(request, "user", None)
            EvidenceVisibilityLog.objects.create(
                evidence=evidence,
                moderator=moderator if moderator is not None and moderator.is_authenticated else None,
                action=action,
                from_visibility=from_visibility,
                to_visibility=visibility,
                note=note,
            )

    @admin.action(description="Mark selected evidence public")
    def mark_public(self, request, queryset):
        self._set_visibility(request, queryset, visibility=Evidence.Visibility.PUBLIC, action=EvidenceVisibilityLog.Action.MARK_PUBLIC)

    @admin.action(description="Mark selected evidence private")
    def mark_private(self, request, queryset):
        self._set_visibility(request, queryset, visibility=Evidence.Visibility.PRIVATE, action=EvidenceVisibilityLog.Action.MARK_PRIVATE)

    @admin.action(description="Mark selected evidence admin-only")
    def mark_admin_only(self, request, queryset):
        self._set_visibility(request, queryset, visibility=Evidence.Visibility.ADMIN_ONLY, action=EvidenceVisibilityLog.Action.MARK_ADMIN_ONLY)


@admin.register(EvidenceVisibilityLog)
class EvidenceVisibilityLogAdmin(admin.ModelAdmin):
    list_display = ("evidence", "action", "from_visibility", "to_visibility", "moderator", "created_at")
    list_filter = ("action", "from_visibility", "to_visibility", "created_at")
    search_fields = ("evidence__company__name", "evidence__title", "moderator__username", "note")
    readonly_fields = ("evidence", "moderator", "action", "from_visibility", "to_visibility", "note", "created_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
