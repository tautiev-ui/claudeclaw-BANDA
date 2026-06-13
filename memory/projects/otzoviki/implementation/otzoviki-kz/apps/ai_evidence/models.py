from django.conf import settings
from django.db import models

from apps.companies.models import Company


class PublicAIYandexEvidenceLogQuerySet(models.QuerySet):
    def public(self):
        return self.filter(visibility=AIYandexEvidenceLog.Visibility.PUBLIC, screenshot="").select_related("company").order_by("-captured_at")


class AIYandexEvidenceLog(models.Model):
    class Platform(models.TextChoices):
        YANDEX_SEARCH = "yandex_search", "Yandex Search"
        YANDEX_NEURO = "yandex_neuro", "Yandex Neuro"
        ALICE = "alice", "Alice"
        AI_OVERVIEW = "ai_overview", "AI Overview"
        OTHER = "other", "Other"

    class Sentiment(models.TextChoices):
        POSITIVE = "positive", "Positive"
        NEUTRAL = "neutral", "Neutral"
        MIXED = "mixed", "Mixed"
        NEGATIVE = "negative", "Negative"
        UNKNOWN = "unknown", "Unknown"

    class Visibility(models.TextChoices):
        PUBLIC = "public", "Public"
        PRIVATE = "private", "Private"
        ADMIN_ONLY = "admin_only", "Admin only"

    YANDEX_SURFACES = {Platform.YANDEX_SEARCH, Platform.YANDEX_NEURO, Platform.ALICE}

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="ai_yandex_evidence_logs")
    platform = models.CharField(max_length=32, choices=Platform.choices)
    query = models.CharField(max_length=500)
    region = models.CharField(max_length=160)
    answer_excerpt = models.TextField(blank=True)
    cited_sources = models.JSONField(default=list, blank=True)
    sentiment = models.CharField(max_length=16, choices=Sentiment.choices, default=Sentiment.UNKNOWN)
    visibility = models.CharField(max_length=16, choices=Visibility.choices, default=Visibility.PRIVATE)
    screenshot = models.FileField(upload_to="ai-evidence/", blank=True)
    captured_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PublicAIYandexEvidenceLogQuerySet.as_manager()

    class Meta:
        ordering = ["-captured_at"]
        indexes = [models.Index(fields=["company", "platform", "region"])]

    def __str__(self):
        return f"{self.company.name} · {self.platform} · {self.query} · {self.region}"

    @property
    def is_public_safe(self) -> bool:
        return self.visibility == self.Visibility.PUBLIC and not self.screenshot

    @property
    def has_yandex_surface(self) -> bool:
        return self.platform in self.YANDEX_SURFACES


class AIYandexEvidenceVisibilityLog(models.Model):
    class Action(models.TextChoices):
        MARK_PUBLIC = "mark_public", "Mark public"
        MARK_PRIVATE = "mark_private", "Mark private"
        MARK_ADMIN_ONLY = "mark_admin_only", "Mark admin only"
        UPDATED = "updated", "Updated"

    log = models.ForeignKey(AIYandexEvidenceLog, on_delete=models.CASCADE, related_name="visibility_logs")
    moderator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="ai_yandex_evidence_visibility_logs")
    action = models.CharField(max_length=32, choices=Action.choices)
    from_visibility = models.CharField(max_length=16, blank=True)
    to_visibility = models.CharField(max_length=16, blank=True)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"{self.log.company.name} · {self.log.platform} · {self.action}"
