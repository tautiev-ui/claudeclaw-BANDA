import secrets

from django.db import models
from django.db.models import F

from apps.companies.models import Company


def generate_qr_token() -> str:
    return secrets.token_urlsafe(12)


class QRReviewFlow(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="qr_review_flows")
    token = models.SlugField(max_length=64, unique=True, default=generate_qr_token)
    label = models.CharField(max_length=160)
    is_active = models.BooleanField(default=True)
    sentiment_filter_enabled = models.BooleanField(default=False)
    scan_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["company__name", "label"]

    def __str__(self):
        return f"{self.company.name} · {self.label}"

    def save(self, *args, **kwargs):
        self.sentiment_filter_enabled = False
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return f"/r/{self.token}/"

    @property
    def robots_meta(self) -> str:
        return "noindex,follow"


class ReviewPlatformLink(models.Model):
    class Platform(models.TextChoices):
        OTZOVIKI = "otzoviki", "Otzoviki"
        YANDEX = "yandex", "Yandex"
        TWO_GIS = "2gis", "2GIS"
        GOOGLE = "google", "Google"
        OTHER = "other", "Other"

    class Capability(models.TextChoices):
        DIRECT_FORM = "direct_form", "Direct form"
        PROFILE = "profile", "Profile"
        MANUAL = "manual", "Manual"
        UNKNOWN = "unknown", "Unknown"

    flow = models.ForeignKey(QRReviewFlow, on_delete=models.CASCADE, related_name="platform_links")
    platform = models.CharField(max_length=16, choices=Platform.choices)
    capability = models.CharField(max_length=16, choices=Capability.choices, default=Capability.UNKNOWN)
    url = models.URLField()
    is_active = models.BooleanField(default=True)
    click_count = models.PositiveIntegerField(default=0)
    last_checked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["flow__company__name", "platform"]
        constraints = [
            models.UniqueConstraint(fields=["flow", "platform"], name="unique_qr_platform_per_flow")
        ]

    def __str__(self):
        return f"{self.flow.company.name} · {self.platform_label}"

    @property
    def platform_label(self) -> str:
        return self.Platform(self.platform).label

    @property
    def is_usable(self) -> bool:
        return self.is_active and self.capability != self.Capability.UNKNOWN and bool(self.url)

    def register_click(self):
        type(self).objects.filter(pk=self.pk).update(click_count=F("click_count") + 1)


class QRScanEventManager(models.Manager):
    def record_scan(self, flow: QRReviewFlow, user_agent_family: str = ""):
        event = self.create(flow=flow, user_agent_family=user_agent_family)
        QRReviewFlow.objects.filter(pk=flow.pk).update(scan_count=F("scan_count") + 1)
        return event


class QRScanEvent(models.Model):
    flow = models.ForeignKey(QRReviewFlow, on_delete=models.CASCADE, related_name="scan_events")
    user_agent_family = models.CharField(max_length=120, blank=True)
    visitor_ip_hash = models.CharField(max_length=128, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = QRScanEventManager()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.flow.company.name} · scan · {self.created_at:%Y-%m-%d}"
