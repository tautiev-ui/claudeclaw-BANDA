from django.db import models
from django.utils import timezone

from apps.editorial.models import Author, MethodologyVersion
from apps.seo.models import SEOFieldsMixin


class GuideCategory(models.Model):
    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True)
    description = models.TextField(blank=True)
    position = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["position", "name"]
        verbose_name_plural = "guide categories"

    def __str__(self):
        return self.name

    def get_absolute_url(self) -> str:
        return f"/kz/guides/#{self.slug}"


class PublicGuideQuerySet(models.QuerySet):
    def public(self):
        return self.filter(status=Guide.Status.PUBLISHED).select_related("category", "author", "methodology")


class Guide(SEOFieldsMixin):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    category = models.ForeignKey(GuideCategory, on_delete=models.PROTECT, related_name="guides")
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, blank=True, related_name="guides")
    methodology = models.ForeignKey(
        MethodologyVersion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="guides",
    )
    title = models.CharField(max_length=240)
    slug = models.SlugField(max_length=260, unique=True)
    summary = models.TextField(blank=True)
    body = models.TextField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    published_at = models.DateTimeField(null=True, blank=True)
    last_verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PublicGuideQuerySet.as_manager()

    class Meta:
        ordering = ["-published_at", "title"]

    def save(self, *args, **kwargs):
        if self.status == self.Status.PUBLISHED and self.published_at is None:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self) -> str:
        return f"/kz/guides/{self.slug}/"

    @property
    def is_public(self) -> bool:
        return self.status == self.Status.PUBLISHED

    @property
    def quality_issues(self) -> list[str]:
        issues = []
        normalized = f"{self.title} {self.summary} {self.body}".lower()
        generic_phrases = (
            "в современном мире",
            "в данной статье",
            "мы рассмотрим основные аспекты",
            "играет важную роль",
            "является важной задачей",
        )
        if any(phrase in normalized for phrase in generic_phrases):
            issues.append("generic_ai_filler")
        if not self.source_references.exists():
            issues.append("missing_source_reference")
        if not self.internal_links.filter(target_type__in=GuideInternalLink.MONEY_PAGE_TYPES).exists():
            issues.append("missing_money_page_link")
        if not self.checklist_items.exists():
            issues.append("missing_checklist")
        if not self.risk_items.exists():
            issues.append("missing_risk_mitigation")
        if not self.faq_items.exists():
            issues.append("missing_faq")
        return issues

    @property
    def is_launch_ready(self) -> bool:
        return self.is_public and not self.quality_issues

    @property
    def quality_gated_robots_meta(self) -> str:
        if not self.is_launch_ready:
            return "noindex,follow"
        return self.robots_meta


class GuideChecklistItem(models.Model):
    guide = models.ForeignKey(Guide, on_delete=models.CASCADE, related_name="checklist_items")
    position = models.PositiveIntegerField(default=0)
    text = models.TextField()

    class Meta:
        ordering = ["position", "id"]

    def __str__(self):
        return f"{self.guide.title} · checklist {self.position}"


class GuideRiskItem(models.Model):
    guide = models.ForeignKey(Guide, on_delete=models.CASCADE, related_name="risk_items")
    position = models.PositiveIntegerField(default=0)
    risk = models.CharField(max_length=240)
    mitigation = models.TextField()

    class Meta:
        ordering = ["position", "id"]

    def __str__(self):
        return f"{self.guide.title} · {self.risk}"


class GuideFAQ(models.Model):
    guide = models.ForeignKey(Guide, on_delete=models.CASCADE, related_name="faq_items")
    position = models.PositiveIntegerField(default=0)
    question = models.CharField(max_length=260)
    answer = models.TextField()

    class Meta:
        ordering = ["position", "id"]
        verbose_name = "guide FAQ"
        verbose_name_plural = "guide FAQs"

    def __str__(self):
        return f"{self.guide.title} · {self.question}"


class GuideSourceReference(models.Model):
    class SourceType(models.TextChoices):
        POLICY = "policy", "Policy"
        LAW = "law", "Law"
        DATA = "data", "Data"
        EDITORIAL = "editorial", "Editorial"
        OTHER = "other", "Other"

    guide = models.ForeignKey(Guide, on_delete=models.CASCADE, related_name="source_references")
    label = models.CharField(max_length=240)
    url = models.URLField()
    source_type = models.CharField(max_length=16, choices=SourceType.choices, default=SourceType.OTHER)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["position", "label"]

    def __str__(self):
        return f"{self.guide.title} · {self.label}"

    @property
    def is_external(self) -> bool:
        return self.url.startswith("http://") or self.url.startswith("https://")


class GuideInternalLink(models.Model):
    class TargetType(models.TextChoices):
        COMPANY = "company", "Company"
        CITY_SERVICE = "city_service", "City service"
        RANKING = "ranking", "Ranking"
        PRICE = "price", "Price"
        GUIDE = "guide", "Guide"
        OTHER = "other", "Other"

    MONEY_PAGE_TYPES = {TargetType.COMPANY, TargetType.CITY_SERVICE, TargetType.RANKING, TargetType.PRICE}

    guide = models.ForeignKey(Guide, on_delete=models.CASCADE, related_name="internal_links")
    label = models.CharField(max_length=240)
    url = models.CharField(max_length=300)
    target_type = models.CharField(max_length=24, choices=TargetType.choices, default=TargetType.OTHER)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["position", "label"]

    def __str__(self):
        return f"{self.guide.title} → {self.label}"

    @property
    def is_money_page(self) -> bool:
        return self.target_type in self.MONEY_PAGE_TYPES
