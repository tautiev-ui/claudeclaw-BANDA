from django.contrib import admin

from apps.ai_evidence.models import AIYandexEvidenceLog, AIYandexEvidenceVisibilityLog


class AIYandexEvidenceVisibilityLogInline(admin.TabularInline):
    model = AIYandexEvidenceVisibilityLog
    extra = 0
    readonly_fields = ("moderator", "action", "from_visibility", "to_visibility", "note", "created_at")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(AIYandexEvidenceLog)
class AIYandexEvidenceLogAdmin(admin.ModelAdmin):
    list_display = ("company", "platform", "query", "region", "sentiment", "visibility", "captured_at")
    list_filter = ("platform", "sentiment", "visibility", "region")
    search_fields = ("company__name", "query", "answer_excerpt", "region")
    readonly_fields = ("captured_at", "updated_at")
    actions = ("mark_public", "mark_private", "mark_admin_only")
    inlines = (AIYandexEvidenceVisibilityLogInline,)

    def _set_visibility(self, request, queryset, *, visibility: str, action: str, note: str = ""):
        for log in queryset:
            if visibility == AIYandexEvidenceLog.Visibility.PUBLIC and log.screenshot:
                continue
            from_visibility = log.visibility
            log.visibility = visibility
            log.save(update_fields=["visibility", "updated_at"])
            moderator = getattr(request, "user", None)
            AIYandexEvidenceVisibilityLog.objects.create(
                log=log,
                moderator=moderator if moderator is not None and moderator.is_authenticated else None,
                action=action,
                from_visibility=from_visibility,
                to_visibility=visibility,
                note=note,
            )

    @admin.action(description="Mark selected AI/Yandex evidence public")
    def mark_public(self, request, queryset):
        self._set_visibility(request, queryset, visibility=AIYandexEvidenceLog.Visibility.PUBLIC, action=AIYandexEvidenceVisibilityLog.Action.MARK_PUBLIC)

    @admin.action(description="Mark selected AI/Yandex evidence private")
    def mark_private(self, request, queryset):
        self._set_visibility(request, queryset, visibility=AIYandexEvidenceLog.Visibility.PRIVATE, action=AIYandexEvidenceVisibilityLog.Action.MARK_PRIVATE)

    @admin.action(description="Mark selected AI/Yandex evidence admin-only")
    def mark_admin_only(self, request, queryset):
        self._set_visibility(request, queryset, visibility=AIYandexEvidenceLog.Visibility.ADMIN_ONLY, action=AIYandexEvidenceVisibilityLog.Action.MARK_ADMIN_ONLY)


@admin.register(AIYandexEvidenceVisibilityLog)
class AIYandexEvidenceVisibilityLogAdmin(admin.ModelAdmin):
    list_display = ("log", "action", "from_visibility", "to_visibility", "moderator", "created_at")
    list_filter = ("action", "from_visibility", "to_visibility", "created_at")
    search_fields = ("log__company__name", "log__query", "log__answer_excerpt", "moderator__username", "note")
    readonly_fields = ("log", "moderator", "action", "from_visibility", "to_visibility", "note", "created_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
