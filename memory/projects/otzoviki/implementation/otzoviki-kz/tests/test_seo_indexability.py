from datetime import timedelta

from django.db import models
from django.test import RequestFactory, SimpleTestCase, override_settings
from django.utils import timezone

from apps.seo.indexability import IndexabilityDecision, IndexabilityStatus
from apps.seo.models import SEOFieldsMixin
from apps.seo.utils import build_absolute_canonical_url, normalize_canonical_path


class DummySEOPage(SEOFieldsMixin, models.Model):
    class Meta:
        app_label = "tests"

    def get_absolute_url(self):
        return "/kz/company/test-company/"


class SEOIndexabilityTests(SimpleTestCase):
    def test_normalize_canonical_path_enforces_leading_and_trailing_slash(self):
        assert normalize_canonical_path("kz/company/test") == "/kz/company/test/"
        assert normalize_canonical_path("/kz/company/test?utm=1") == "/kz/company/test/"
        assert normalize_canonical_path("/") == "/"

    @override_settings(ALLOWED_HOSTS=["otzoviki.kz"])
    def test_build_absolute_canonical_url_uses_request_host_and_https_when_secure(self):
        request = RequestFactory().get("/anything/", secure=True, HTTP_HOST="otzoviki.kz")
        assert build_absolute_canonical_url(request, "kz/company/test") == "https://otzoviki.kz/kz/company/test/"

    def test_indexability_blocks_draft_pages(self):
        page = DummySEOPage(index_status=IndexabilityStatus.DRAFT)
        decision = page.get_indexability_decision()
        assert decision == IndexabilityDecision(False, "draft")
        assert page.robots_meta == "noindex,follow"

    def test_indexability_blocks_pages_without_trust_data(self):
        page = DummySEOPage(
            index_status=IndexabilityStatus.INDEXABLE,
            seo_title="Test company reviews",
            seo_description="Useful company reputation dossier",
            methodology_version="v1",
        )
        decision = page.get_indexability_decision(require_trust_data=True)
        assert decision.allowed is False
        assert decision.reason == "missing_trust_data"

    def test_indexability_allows_filled_page_with_fresh_trust_data(self):
        page = DummySEOPage(
            index_status=IndexabilityStatus.INDEXABLE,
            seo_title="Test company reviews",
            seo_description="Useful company reputation dossier",
            source_count=3,
            last_verified_at=timezone.now() - timedelta(days=1),
            methodology_version="v1",
        )
        decision = page.get_indexability_decision(require_trust_data=True)
        assert decision == IndexabilityDecision(True, "indexable")
        assert page.robots_meta == "index,follow"
        assert page.schema_eligible is True

    def test_indexability_blocks_stale_verified_pages(self):
        page = DummySEOPage(
            index_status=IndexabilityStatus.INDEXABLE,
            seo_title="Test company reviews",
            seo_description="Useful company reputation dossier",
            source_count=3,
            last_verified_at=timezone.now() - timedelta(days=120),
            methodology_version="v1",
        )
        decision = page.get_indexability_decision(require_trust_data=True, max_age_days=90)
        assert decision.allowed is False
        assert decision.reason == "stale_trust_data"
