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
def test_verified_company_first_index_batch_exports_csv_and_html_staff_only(client):
    country = Country.objects.create(code="KZ", name="Казахстан", slug="kz")
    city = City.objects.create(country=country, name="Алматы", slug="almaty")
    category = ServiceCategory.objects.create(name="Ремонт", slug="remont")
    service = Service.objects.create(category=category, name="Ремонт квартир", slug="remont-kvartir")
    company = Company.objects.create(
        name="Verified Remont",
        slug="verified-remont",
        short_description="Проверенная компания для первой индексации.",
        index_status=IndexabilityStatus.INDEXABLE.value,
        seo_title="Verified Remont отзывы",
        seo_description="Проверенная компания для первой индексации.",
        canonical_path="/kz/company/verified-remont/",
        source_count=2,
        last_verified_at=timezone.now(),
        methodology_version="company-dossier-trust-gate-v1",
    )
    CompanyService.objects.create(company=company, city=city, service=service, is_primary=True)
    ExternalSource.objects.create(company=company, source_type=ExternalSource.SourceType.YANDEX, name="Яндекс Бизнес", url="https://yandex.ru/maps/org/verified", same_as_verified=True, captured_at=timezone.now())
    ExternalSource.objects.create(company=company, source_type=ExternalSource.SourceType.TWO_GIS, name="2ГИС", url="https://2gis.kz/almaty/firm/verified", same_as_verified=True, captured_at=timezone.now())

    anonymous_csv = client.get("/admin/launch-qa/verified-company-first-index-batch.csv")
    anonymous_html = client.get("/admin/launch-qa/verified-company-first-index-batch/")
    assert anonymous_csv.status_code == 302
    assert anonymous_html.status_code == 302
    assert "/admin/login/" in anonymous_csv["Location"]

    staff = get_user_model().objects.create_user(username="first-index-verified", password="pass", is_staff=True)
    client.force_login(staff)

    csv_response = client.get("/admin/launch-qa/verified-company-first-index-batch.csv")
    html_response = client.get("/admin/launch-qa/verified-company-first-index-batch/")

    assert csv_response.status_code == 200
    assert csv_response["Content-Type"] == "text/csv; charset=utf-8"
    assert csv_response["Content-Disposition"] == 'attachment; filename="verified-company-first-index-batch.csv"'
    rows = list(csv.DictReader(io.StringIO(csv_response.content.decode())))
    assert len(rows) == 1
    row = rows[0]
    assert row["url"] == "/kz/company/verified-remont/"
    assert row["name"] == "Verified Remont"
    assert row["source_count"] == "2"
    assert row["yandex_url"] == "https://yandex.ru/maps/org/verified"
    assert row["two_gis_url"] == "https://2gis.kz/almaty/firm/verified"
    assert row["robots_expected"] == "index,follow"
    assert row["canonical_path"] == "/kz/company/verified-remont/"
    assert row["smoke_status"] == "pending-production-smoke"
    assert row["submission_allowed"] == "true"
    assert row["manual_required"] == "true"

    html = html_response.content.decode()
    assert html_response.status_code == 200
    assert "Verified company first-index batch" in html
    assert "/kz/company/verified-remont/" in html
    assert "https://yandex.ru/maps/org/verified" in html
    assert "https://2gis.kz/almaty/firm/verified" in html
    assert "pending-production-smoke" in html
