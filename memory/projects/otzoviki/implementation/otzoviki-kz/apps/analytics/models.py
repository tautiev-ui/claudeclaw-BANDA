import re

from django.db import models

from apps.companies.models import Company


class AnalyticsEvent(models.Model):
    class EventType(models.TextChoices):
        SEARCH = "search", "Search"
        COMPANY_DOSSIER_OPEN = "company_dossier_open", "Company dossier open"
        REVIEW_SUBMIT_START = "review_submit_start", "Review submit start"
        REVIEW_SUBMIT_COMPLETE = "review_submit_complete", "Review submit complete"
        CLAIM_PROFILE_CLICK = "claim_profile_click", "Claim profile click"
        CLAIM_PROFILE_SUBMIT = "claim_profile_submit", "Claim profile submit"
        AUDIT_LEAD_SUBMIT = "audit_lead_submit", "Audit lead submit"
        GUIDE_CTA_CLICK = "guide_cta_click", "Guide CTA click"

    event_type = models.CharField(max_length=48, choices=EventType.choices, db_index=True)
    path = models.CharField(max_length=500, blank=True)
    query = models.CharField(max_length=500, blank=True)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, related_name="analytics_events")
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [models.Index(fields=["event_type", "created_at"])]

    def __str__(self):
        return f"{self.event_type} · {self.path or self.query or self.company_id or ''}"


EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)
PHONE_RE = re.compile(r"(?<!\w)\+?\d[\d\s().-]{7,}\d(?!\w)")
SENSITIVE_METADATA_KEYS = {"email", "contact_email", "phone", "contact_phone", "token", "secret", "password"}


def sanitize_query(value: str) -> str:
    value = EMAIL_RE.sub("[email]", value or "")
    value = PHONE_RE.sub("[phone]", value)
    return value[:500]


def sanitize_metadata(value):
    if isinstance(value, dict):
        sanitized = {}
        for key, item in value.items():
            if key.lower() in SENSITIVE_METADATA_KEYS:
                sanitized[key] = "[redacted]"
            else:
                sanitized[key] = sanitize_metadata(item)
        return sanitized
    if isinstance(value, list):
        return [sanitize_metadata(item) for item in value]
    if isinstance(value, str):
        return sanitize_query(value)
    return value


def track_event(*, event_type: str, request=None, company: Company | None = None, query: str = "", metadata: dict | None = None) -> AnalyticsEvent:
    path = request.path if request is not None else ""
    return AnalyticsEvent.objects.create(
        event_type=event_type,
        path=path,
        query=sanitize_query(query),
        company=company,
        metadata=sanitize_metadata(metadata or {}),
    )
