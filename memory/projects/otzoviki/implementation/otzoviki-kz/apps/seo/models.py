from django.db import models
from django.utils import timezone

from .indexability import IndexabilityDecision, IndexabilityStatus
from .utils import normalize_canonical_path


class SEOFieldsMixin(models.Model):
    """Abstract SEO/indexability fields shared by indexable public page models.

    The mixin keeps Stage 9B trust gates close to the data model: a page can be
    technically published but still return noindex when trust/evidence data is
    missing or stale.
    """

    index_status = models.CharField(
        max_length=16,
        choices=[(status.value, status.value) for status in IndexabilityStatus],
        default=IndexabilityStatus.DRAFT,
    )
    seo_title = models.CharField(max_length=255, blank=True)
    seo_description = models.TextField(blank=True)
    canonical_path = models.CharField(max_length=512, blank=True)
    source_count = models.PositiveIntegerField(default=0)
    last_verified_at = models.DateTimeField(null=True, blank=True)
    methodology_version = models.CharField(max_length=64, blank=True)
    allow_schema = models.BooleanField(default=True)

    class Meta:
        abstract = True

    @property
    def canonical_url_path(self) -> str:
        if self.canonical_path:
            return normalize_canonical_path(self.canonical_path)
        get_absolute_url = getattr(self, "get_absolute_url", None)
        if callable(get_absolute_url):
            return normalize_canonical_path(get_absolute_url())
        return "/"

    @property
    def robots_meta(self) -> str:
        return "index,follow" if self.get_indexability_decision().allowed else "noindex,follow"

    @property
    def schema_eligible(self) -> bool:
        return self.allow_schema and self.get_indexability_decision(require_trust_data=True).allowed

    def has_required_trust_data(self) -> bool:
        return bool(self.source_count > 0 and self.last_verified_at and self.methodology_version)

    def get_indexability_decision(self, *, require_trust_data: bool = False, max_age_days: int = 90) -> IndexabilityDecision:
        status = IndexabilityStatus(self.index_status)
        if status == IndexabilityStatus.DRAFT:
            return IndexabilityDecision(False, "draft")
        if status == IndexabilityStatus.NOINDEX:
            return IndexabilityDecision(False, "noindex")
        if not self.seo_title or not self.seo_description:
            return IndexabilityDecision(False, "missing_seo_fields")
        if require_trust_data:
            if not self.has_required_trust_data():
                return IndexabilityDecision(False, "missing_trust_data")
            if self.last_verified_at < timezone.now() - timezone.timedelta(days=max_age_days):
                return IndexabilityDecision(False, "stale_trust_data")
        return IndexabilityDecision(True, "indexable")
