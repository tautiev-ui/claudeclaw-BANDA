import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.companies.models import Company
from apps.evidence.models import ExternalSource
from apps.guides.models import Guide, GuideCategory
from apps.seo.indexability import IndexabilityStatus


@pytest.mark.django_db
def test_freshness_dashboard_requires_staff(client):
    response = client.get("/admin/launch-qa/freshness/")

    assert response.status_code == 302
    assert "/admin/login/" in response["Location"]


@pytest.mark.django_db
def test_freshness_dashboard_shows_stale_dossiers_sources_and_guides(client):
    old = timezone.now() - timezone.timedelta(days=121)
    fresh = timezone.now() - timezone.timedelta(days=5)
    stale_company = Company.objects.create(
        name="Stale Remont",
        slug="stale-remont",
        seo_title="Stale Remont dossier",
        seo_description="Filled dossier",
        index_status=IndexabilityStatus.INDEXABLE,
        source_count=2,
        last_verified_at=old,
        methodology_version="mvp-1",
    )
    fresh_company = Company.objects.create(
        name="Fresh Remont",
        slug="fresh-remont",
        seo_title="Fresh Remont dossier",
        seo_description="Fresh dossier",
        index_status=IndexabilityStatus.INDEXABLE,
        source_count=2,
        last_verified_at=fresh,
        methodology_version="mvp-1",
    )
    ExternalSource.objects.create(
        company=stale_company,
        source_type=ExternalSource.SourceType.YANDEX,
        name="Yandex Maps stale",
        url="https://yandex.kz/maps/org/stale",
        captured_at=old,
    )
    ExternalSource.objects.create(
        company=fresh_company,
        source_type=ExternalSource.SourceType.YANDEX,
        name="Yandex Maps fresh",
        url="https://yandex.kz/maps/org/fresh",
        captured_at=fresh,
    )
    category = GuideCategory.objects.create(name="Проверка", slug="proverka")
    stale_guide = Guide.objects.create(
        category=category,
        title="Stale guide",
        slug="stale-guide",
        body="Body",
        status=Guide.Status.PUBLISHED,
        last_verified_at=old,
    )
    Guide.objects.create(
        category=category,
        title="Fresh guide",
        slug="fresh-guide",
        body="Body",
        status=Guide.Status.PUBLISHED,
        last_verified_at=fresh,
    )
    staff = get_user_model().objects.create_user(username="freshness", password="pass", is_staff=True)
    client.force_login(staff)

    response = client.get("/admin/launch-qa/freshness/")

    assert response.status_code == 200
    html = response.content.decode()
    assert '<meta name="robots" content="noindex,follow">' in html
    assert "Freshness dashboard" in html
    assert "Stale Remont" in html
    assert "Yandex Maps stale" in html
    assert "Stale guide" in html
    assert "Fresh Remont" not in html
    assert "Yandex Maps fresh" not in html
    assert "Fresh guide" not in html
    assert str(stale_guide.get_absolute_url()) in html
    assert "40-gate freshness readiness" in html
    assert "90-day trust cutoff" in html
    assert "Stale dossier risk" in html
    assert "Stale external source risk" in html
    assert "Stale guide risk" in html
    assert "Refresh priority" in html
    assert "Re-verify before index" in html
    assert "Yandex/AI evidence recrawl" in html
    assert "Methodology version drift" in html
    assert "Export stale worklist" in html
