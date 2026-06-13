import csv
import io

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.companies.models import Company, CompanyService
from apps.evidence.models import ExternalSource
from apps.locations.models import City, Country
from apps.seo.indexability import IndexabilityStatus
from apps.services.models import Service, ServiceCategory


@pytest.mark.django_db
def test_company_publish_readiness_csv_is_staff_only_and_reports_gate_reasons(client):
    response = client.get("/admin/companies/publish-readiness.csv")
    assert response.status_code == 302
    assert "/admin/login/" in response["Location"]

    country = Country.objects.create(code="KZ", name="Казахстан", slug="kz", is_active=True)
    city = City.objects.create(country=country, name="Астана", slug="astana", is_active=True)
    category = ServiceCategory.objects.create(name="Ремонт", slug="remont", is_active=True)
    service = Service.objects.create(category=category, name="Ремонт квартир", slug="remont-kvartir", is_active=True)
    ready = Company.objects.create(
        name="Готовая компания",
        slug="ready-company",
        short_description="Проверяемая компания.",
        index_status=IndexabilityStatus.NOINDEX.value,
        seo_title="Готовая компания — досье",
        seo_description="Проверяемая компания.",
        canonical_path="/kz/company/ready-company/",
    )
    blocked = Company.objects.create(
        name="Слабая компания",
        slug="blocked-company",
        short_description="",
        index_status=IndexabilityStatus.NOINDEX.value,
        seo_title="Слабая компания — досье",
        seo_description="",
        canonical_path="/kz/company/blocked-company/",
    )
    CompanyService.objects.create(company=ready, city=city, service=service, is_primary=True)
    now = timezone.now()
    ExternalSource.objects.create(company=ready, source_type=ExternalSource.SourceType.YANDEX, name="Яндекс", url="https://yandex.kz/maps/org/ready", same_as_verified=True, captured_at=now)
    ExternalSource.objects.create(company=ready, source_type=ExternalSource.SourceType.TWO_GIS, name="2ГИС", url="https://2gis.kz/astana/firm/ready", same_as_verified=True, captured_at=now)
    ExternalSource.objects.create(company=blocked, source_type=ExternalSource.SourceType.YANDEX, name="Яндекс", url="https://yandex.kz/maps/org/blocked", same_as_verified=False, captured_at=now)

    staff = get_user_model().objects.create_user(username="publisher", password="pass", is_staff=True)
    client.force_login(staff)
    response = client.get("/admin/companies/publish-readiness.csv")

    assert response.status_code == 200
    assert response["Content-Type"] == "text/csv; charset=utf-8"
    assert response["Content-Disposition"] == 'attachment; filename="company-publish-readiness.csv"'
    rows = list(csv.DictReader(io.StringIO(response.content.decode())))
    by_slug = {row["slug"]: row for row in rows}
    assert by_slug["ready-company"]["status"] == "ready"
    assert by_slug["ready-company"]["verified_sources"] == "2"
    assert by_slug["ready-company"]["would_index"] == "true"
    assert by_slug["blocked-company"]["status"] == "blocked"
    assert "short_description" in by_slug["blocked-company"]["reason"]
    assert by_slug["blocked-company"]["would_index"] == "false"
