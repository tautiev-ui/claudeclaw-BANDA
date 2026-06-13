from django.conf import settings
from django.db import models

from apps.companies.models import Company
from apps.reviews.models import Review


class ExternalSource(models.Model):
    class SourceType(models.TextChoices):
        YANDEX = "yandex", "Яндекс"
        TWO_GIS = "2gis", "2ГИС"
        GOOGLE = "google", "Google"
        WEBSITE = "website", "Сайт"
        OTHER = "other", "Другое"

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="external_sources")
    source_type = models.CharField(max_length=24, choices=SourceType.choices)
    name = models.CharField(max_length=160)
    url = models.URLField()
    same_as_verified = models.BooleanField(default=False)
    captured_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["company__name", "source_type", "name"]
        constraints = [models.UniqueConstraint(fields=["company", "source_type", "url"], name="unique_company_external_source")]

    def __str__(self):
        return f"{self.company.name} · {self.name}"

    @property
    def public_label(self) -> str:
        suffix = "sameAs verified" if self.same_as_verified else "external source"
        return f"{self.name} · {suffix}"


class PublicEvidenceQuerySet(models.QuerySet):
    def public(self):
        return self.filter(visibility=Evidence.Visibility.PUBLIC).exclude(evidence_type=Evidence.EvidenceType.PRIVATE_PROOF).select_related("company").order_by("-captured_at", "title")


class Evidence(models.Model):
    class EvidenceType(models.TextChoices):
        OWNED_REVIEW = "owned_review", "Otzoviki review"
        EXTERNAL_FOOTPRINT = "external_footprint", "External footprint"
        COMPLAINT_SIGNAL = "complaint_signal", "Complaint signal"
        EDITORIAL_NOTE = "editorial_note", "Editorial note"
        PRIVATE_PROOF = "private_proof", "Private proof"

    class Visibility(models.TextChoices):
        PUBLIC = "public", "Public"
        PRIVATE = "private", "Private"
        ADMIN_ONLY = "admin_only", "Admin only"

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="evidence_items")
    review = models.ForeignKey(Review, on_delete=models.SET_NULL, null=True, blank=True, related_name="private_evidence_items")
    external_source = models.ForeignKey(ExternalSource, on_delete=models.SET_NULL, null=True, blank=True, related_name="evidence_items")
    evidence_type = models.CharField(max_length=32, choices=EvidenceType.choices)
    title = models.CharField(max_length=220)
    claim = models.TextField()
    source_url = models.URLField(blank=True)
    visibility = models.CharField(max_length=16, choices=Visibility.choices, default=Visibility.PRIVATE)
    captured_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    objects = PublicEvidenceQuerySet.as_manager()

    class Meta:
        ordering = ["-captured_at", "title"]
        verbose_name_plural = "evidence"

    def __str__(self):
        return f"{self.company.name} · {self.title}"

    @property
    def is_public(self) -> bool:
        return self.visibility == self.Visibility.PUBLIC and self.evidence_type != self.EvidenceType.PRIVATE_PROOF

    @property
    def public_label(self) -> str:
        return f"{self.evidence_type} · {self.title}"


class EvidenceVisibilityLog(models.Model):
    class Action(models.TextChoices):
        MARK_PUBLIC = "mark_public", "Mark public"
        MARK_PRIVATE = "mark_private", "Mark private"
        MARK_ADMIN_ONLY = "mark_admin_only", "Mark admin only"
        UPDATED = "updated", "Updated"

    evidence = models.ForeignKey(Evidence, on_delete=models.CASCADE, related_name="visibility_logs")
    moderator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="evidence_visibility_logs")
    action = models.CharField(max_length=32, choices=Action.choices)
    from_visibility = models.CharField(max_length=16, blank=True)
    to_visibility = models.CharField(max_length=16, blank=True)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"{self.evidence.company.name} · {self.evidence.title} · {self.action}"
