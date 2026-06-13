from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.companies.models import Company


class BusinessAccount(models.Model):
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name="business_account")
    display_name = models.CharField(max_length=220)
    paid_profile_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_name"]

    def __str__(self):
        return self.display_name

    def verified_representatives(self):
        return self.representatives.filter(
            verification_status=BusinessRepresentative.VerificationStatus.APPROVED,
            email_verified=True,
        ).order_by("full_name")

    @property
    def has_verified_representative(self) -> bool:
        return self.verified_representatives().exists()


class BusinessRepresentative(models.Model):
    class VerificationStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    account = models.ForeignKey(BusinessAccount, on_delete=models.CASCADE, related_name="representatives")
    full_name = models.CharField(max_length=160)
    email = models.EmailField()
    role_title = models.CharField(max_length=120, blank=True)
    verification_status = models.CharField(
        max_length=16,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING,
    )
    email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["account__display_name", "full_name"]
        constraints = [
            models.UniqueConstraint(fields=["account", "email"], name="unique_business_rep_email_per_account")
        ]

    def __str__(self):
        return f"{self.full_name} · {self.account.display_name}"

    @property
    def is_verified(self) -> bool:
        return self.verification_status == self.VerificationStatus.APPROVED and self.email_verified

    @property
    def can_manage_profile(self) -> bool:
        return self.is_verified

    @property
    def can_submit_official_response(self) -> bool:
        return self.is_verified


class ClaimProfileRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="claim_requests")
    contact_name = models.CharField(max_length=160)
    contact_email = models.EmailField()
    phone = models.CharField(max_length=64, blank=True)
    proof_note = models.TextField(blank=True)
    source_page = models.CharField(max_length=300, blank=True)
    consent_given = models.BooleanField(default=False)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    decided_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.company.name} · {self.contact_name} · {self.status}"

    def approve(self):
        self.status = self.Status.APPROVED
        self.decided_at = timezone.now()
        self.save(update_fields=["status", "decided_at", "updated_at"])
        self.company.profile_status = Company.ProfileStatus.CLAIMED
        self.company.save(update_fields=["profile_status", "updated_at"])

    def reject(self):
        self.status = self.Status.REJECTED
        self.decided_at = timezone.now()
        self.save(update_fields=["status", "decided_at", "updated_at"])


class ClaimProfileModerationLog(models.Model):
    class Action(models.TextChoices):
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        UPDATED = "updated", "Updated"

    claim = models.ForeignKey(ClaimProfileRequest, on_delete=models.CASCADE, related_name="moderation_logs")
    moderator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="claim_profile_moderation_logs")
    action = models.CharField(max_length=24, choices=Action.choices)
    from_status = models.CharField(max_length=16, blank=True)
    to_status = models.CharField(max_length=16, blank=True)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"{self.claim.company.name} · {self.claim.contact_name} · {self.action}"


class PublicOfficialResponseQuerySet(models.QuerySet):
    def public(self):
        return self.filter(status=OfficialResponse.Status.PUBLISHED).select_related("company", "representative")


class OfficialResponse(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PUBLISHED = "published", "Published"
        REJECTED = "rejected", "Rejected"

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="official_responses")
    representative = models.ForeignKey(
        BusinessRepresentative,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="official_responses",
    )
    body = models.TextField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    source_page = models.CharField(max_length=300, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PublicOfficialResponseQuerySet.as_manager()

    class Meta:
        ordering = ["-published_at", "-created_at"]

    def save(self, *args, **kwargs):
        if self.status == self.Status.PUBLISHED and self.published_at is None:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company.name} · official response · {self.status}"

    @property
    def is_public(self) -> bool:
        return self.status == self.Status.PUBLISHED

    @property
    def right_of_reply_policy_url(self) -> str:
        return "/right-of-reply/"


class OfficialResponseModerationLog(models.Model):
    class Action(models.TextChoices):
        PUBLISHED = "published", "Published"
        REJECTED = "rejected", "Rejected"
        UPDATED = "updated", "Updated"

    response = models.ForeignKey(OfficialResponse, on_delete=models.CASCADE, related_name="moderation_logs")
    moderator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="official_response_moderation_logs")
    action = models.CharField(max_length=24, choices=Action.choices)
    from_status = models.CharField(max_length=16, blank=True)
    to_status = models.CharField(max_length=16, blank=True)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"{self.response.company.name} · official response · {self.action}"


class ReputationAuditLead(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "New"
        CONTACTED = "contacted", "Contacted"
        COMPLETED = "completed", "Completed"
        CLOSED = "closed", "Closed"

    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, related_name="audit_leads")
    contact_name = models.CharField(max_length=160)
    contact_email = models.EmailField()
    phone = models.CharField(max_length=64, blank=True)
    source_page = models.CharField(max_length=300, blank=True)
    requested_surfaces = models.JSONField(default=list, blank=True)
    yandex_visibility_summary = models.TextField(blank=True)
    ai_visibility_summary = models.TextField(blank=True)
    audit_recommendations = models.TextField(blank=True)
    consent_given = models.BooleanField(default=False)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.NEW)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        company_name = self.company.name if self.company else "No company"
        return f"{company_name} · {self.contact_email} · {self.status}"

    @property
    def has_yandex_ai_scope(self) -> bool:
        surfaces = set(self.requested_surfaces or [])
        return bool({"yandex", "ai"} & surfaces)

    @property
    def has_audit_output(self) -> bool:
        return bool(self.yandex_visibility_summary or self.ai_visibility_summary or self.audit_recommendations)

    @property
    def audit_output_text(self) -> str:
        parts = [
            self.yandex_visibility_summary,
            self.ai_visibility_summary,
            self.audit_recommendations,
        ]
        return "\n\n".join(part for part in parts if part)


class ReputationAuditLeadStatusLog(models.Model):
    class Action(models.TextChoices):
        CONTACTED = "contacted", "Contacted"
        COMPLETED = "completed", "Completed"
        CLOSED = "closed", "Closed"
        UPDATED = "updated", "Updated"

    lead = models.ForeignKey(ReputationAuditLead, on_delete=models.CASCADE, related_name="status_logs")
    moderator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="reputation_audit_status_logs")
    action = models.CharField(max_length=24, choices=Action.choices)
    from_status = models.CharField(max_length=16, blank=True)
    to_status = models.CharField(max_length=16, blank=True)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"{self.lead.contact_email} · audit lead · {self.action}"
