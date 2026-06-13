import pytest
from django.contrib.admin.sites import AdminSite
from django.utils import timezone

from apps.companies.admin import CompanyAdmin
from apps.companies.models import Company
from apps.seo.admin_helpers import freshness_badge, indexability_badge, required_trust_fields_missing
from apps.seo.indexability import IndexabilityStatus


@pytest.mark.django_db
def test_indexability_badge_reports_allowed_and_reason_for_admin():
    company = Company.objects.create(
        name="Alma Remont",
        slug="alma-remont",
        index_status=IndexabilityStatus.INDEXABLE,
        seo_title="Alma Remont отзывы",
        seo_description="Досье Alma Remont",
        source_count=2,
        last_verified_at=timezone.now(),
        methodology_version="2026.1",
    )

    assert indexability_badge(company) == "✅ indexable"
    assert freshness_badge(company) == "✅ fresh"
    assert required_trust_fields_missing(company) == []


@pytest.mark.django_db
def test_indexability_badge_lists_missing_trust_fields_and_stale_state():
    stale = timezone.now() - timezone.timedelta(days=120)
    company = Company.objects.create(
        name="Stale Remont",
        slug="stale-remont",
        index_status=IndexabilityStatus.INDEXABLE,
        seo_title="Stale",
        seo_description="Stale desc",
        source_count=0,
        last_verified_at=stale,
        methodology_version="",
    )

    assert indexability_badge(company) == "🚫 missing_trust_data"
    assert freshness_badge(company) == "⚠️ stale"
    assert required_trust_fields_missing(company) == ["source_count", "methodology_version"]


@pytest.mark.django_db
def test_company_admin_exposes_indexability_and_freshness_columns():
    admin = CompanyAdmin(Company, AdminSite())

    assert "indexability" in admin.list_display
    assert "freshness" in admin.list_display
