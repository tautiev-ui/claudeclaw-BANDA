from django.contrib import admin

from apps.business.models import (
    BusinessAccount,
    BusinessRepresentative,
    ClaimProfileModerationLog,
    ClaimProfileRequest,
    OfficialResponse,
    OfficialResponseModerationLog,
    ReputationAuditLead,
    ReputationAuditLeadStatusLog,
)


@admin.register(BusinessAccount)
class BusinessAccountAdmin(admin.ModelAdmin):
    list_display = ("display_name", "company", "paid_profile_active", "updated_at")
    list_filter = ("paid_profile_active",)
    search_fields = ("display_name", "company__name")


@admin.register(BusinessRepresentative)
class BusinessRepresentativeAdmin(admin.ModelAdmin):
    list_display = ("full_name", "account", "email", "verification_status", "email_verified")
    list_filter = ("verification_status", "email_verified")
    search_fields = ("full_name", "email", "account__display_name", "account__company__name")


class ClaimProfileModerationLogInline(admin.TabularInline):
    model = ClaimProfileModerationLog
    extra = 0
    readonly_fields = ("moderator", "action", "from_status", "to_status", "note", "created_at")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(ClaimProfileRequest)
class ClaimProfileRequestAdmin(admin.ModelAdmin):
    list_display = ("company", "contact_name", "contact_email", "status", "consent_given", "created_at")
    list_filter = ("status", "consent_given")
    search_fields = ("company__name", "contact_name", "contact_email", "phone")
    actions = ("mark_approved", "mark_rejected")
    inlines = (ClaimProfileModerationLogInline,)

    def _moderate(self, request, queryset, *, status: str, action: str, note: str = ""):
        for claim in queryset:
            from_status = claim.status
            if status == ClaimProfileRequest.Status.APPROVED:
                claim.approve()
            else:
                claim.reject()
            moderator = getattr(request, "user", None)
            ClaimProfileModerationLog.objects.create(
                claim=claim,
                moderator=moderator if moderator is not None and moderator.is_authenticated else None,
                action=action,
                from_status=from_status,
                to_status=status,
                note=note,
            )

    @admin.action(description="Approve selected profile claims")
    def mark_approved(self, request, queryset):
        self._moderate(request, queryset, status=ClaimProfileRequest.Status.APPROVED, action=ClaimProfileModerationLog.Action.APPROVED)

    @admin.action(description="Reject selected profile claims")
    def mark_rejected(self, request, queryset):
        self._moderate(request, queryset, status=ClaimProfileRequest.Status.REJECTED, action=ClaimProfileModerationLog.Action.REJECTED)


@admin.register(ClaimProfileModerationLog)
class ClaimProfileModerationLogAdmin(admin.ModelAdmin):
    list_display = ("claim", "action", "from_status", "to_status", "moderator", "created_at")
    list_filter = ("action", "from_status", "to_status", "created_at")
    search_fields = ("claim__company__name", "claim__contact_name", "claim__contact_email", "moderator__username", "note")
    readonly_fields = ("claim", "moderator", "action", "from_status", "to_status", "note", "created_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class OfficialResponseModerationLogInline(admin.TabularInline):
    model = OfficialResponseModerationLog
    extra = 0
    readonly_fields = ("moderator", "action", "from_status", "to_status", "note", "created_at")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(OfficialResponse)
class OfficialResponseAdmin(admin.ModelAdmin):
    list_display = ("company", "representative", "status", "published_at", "created_at")
    list_filter = ("status",)
    search_fields = ("company__name", "representative__full_name", "body")
    actions = ("mark_published", "mark_rejected")
    inlines = (OfficialResponseModerationLogInline,)

    def _moderate(self, request, queryset, *, status: str, action: str, note: str = ""):
        for response in queryset:
            from_status = response.status
            response.status = status
            if status == OfficialResponse.Status.PUBLISHED:
                response.save()
            else:
                response.published_at = None
                response.save(update_fields=["status", "published_at", "updated_at"])
            moderator = getattr(request, "user", None)
            OfficialResponseModerationLog.objects.create(
                response=response,
                moderator=moderator if moderator is not None and moderator.is_authenticated else None,
                action=action,
                from_status=from_status,
                to_status=status,
                note=note,
            )

    @admin.action(description="Publish selected official responses")
    def mark_published(self, request, queryset):
        self._moderate(request, queryset, status=OfficialResponse.Status.PUBLISHED, action=OfficialResponseModerationLog.Action.PUBLISHED)

    @admin.action(description="Reject selected official responses")
    def mark_rejected(self, request, queryset):
        self._moderate(request, queryset, status=OfficialResponse.Status.REJECTED, action=OfficialResponseModerationLog.Action.REJECTED)


@admin.register(OfficialResponseModerationLog)
class OfficialResponseModerationLogAdmin(admin.ModelAdmin):
    list_display = ("response", "action", "from_status", "to_status", "moderator", "created_at")
    list_filter = ("action", "from_status", "to_status", "created_at")
    search_fields = ("response__company__name", "response__body", "moderator__username", "note")
    readonly_fields = ("response", "moderator", "action", "from_status", "to_status", "note", "created_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class ReputationAuditLeadStatusLogInline(admin.TabularInline):
    model = ReputationAuditLeadStatusLog
    extra = 0
    readonly_fields = ("moderator", "action", "from_status", "to_status", "note", "created_at")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(ReputationAuditLead)
class ReputationAuditLeadAdmin(admin.ModelAdmin):
    list_display = ("company", "contact_name", "contact_email", "status", "has_output", "consent_given", "created_at")
    list_filter = ("status", "consent_given")
    search_fields = (
        "company__name",
        "contact_name",
        "contact_email",
        "phone",
        "yandex_visibility_summary",
        "ai_visibility_summary",
        "audit_recommendations",
    )
    fieldsets = (
        (None, {"fields": ("company", "contact_name", "contact_email", "phone", "source_page", "requested_surfaces", "consent_given", "status")}),
        ("Audit output", {"fields": ("yandex_visibility_summary", "ai_visibility_summary", "audit_recommendations")}),
    )
    actions = ("mark_contacted", "mark_completed", "mark_closed")
    inlines = (ReputationAuditLeadStatusLogInline,)

    def _set_status(self, request, queryset, *, status: str, action: str, note: str = ""):
        for lead in queryset:
            from_status = lead.status
            lead.status = status
            lead.save(update_fields=["status", "updated_at"])
            moderator = getattr(request, "user", None)
            ReputationAuditLeadStatusLog.objects.create(
                lead=lead,
                moderator=moderator if moderator is not None and moderator.is_authenticated else None,
                action=action,
                from_status=from_status,
                to_status=status,
                note=note,
            )

    @admin.action(description="Mark selected audit leads as contacted")
    def mark_contacted(self, request, queryset):
        self._set_status(request, queryset, status=ReputationAuditLead.Status.CONTACTED, action=ReputationAuditLeadStatusLog.Action.CONTACTED)

    @admin.action(description="Mark selected audit leads as completed")
    def mark_completed(self, request, queryset):
        self._set_status(request, queryset, status=ReputationAuditLead.Status.COMPLETED, action=ReputationAuditLeadStatusLog.Action.COMPLETED)

    @admin.action(description="Close selected audit leads")
    def mark_closed(self, request, queryset):
        self._set_status(request, queryset, status=ReputationAuditLead.Status.CLOSED, action=ReputationAuditLeadStatusLog.Action.CLOSED)

    @admin.display(boolean=True, description="Output")
    def has_output(self, obj):
        return obj.has_audit_output


@admin.register(ReputationAuditLeadStatusLog)
class ReputationAuditLeadStatusLogAdmin(admin.ModelAdmin):
    list_display = ("lead", "action", "from_status", "to_status", "moderator", "created_at")
    list_filter = ("action", "from_status", "to_status", "created_at")
    search_fields = ("lead__company__name", "lead__contact_name", "lead__contact_email", "moderator__username", "note")
    readonly_fields = ("lead", "moderator", "action", "from_status", "to_status", "note", "created_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
