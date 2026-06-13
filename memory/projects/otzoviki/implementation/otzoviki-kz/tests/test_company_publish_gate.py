import csv
import io

import pytest
from django.core.management import call_command
from django.utils import timezone

from apps.companies.models import Company, CompanyService
from apps.evidence.models import ExternalSource
from apps.locations.models import City, Country
from apps.seo.indexability import IndexabilityStatus
from apps.services.models import Service, ServiceCategory


@pytest.fixture
def service_context():
    country = Country.objects.create(code="KZ", name="Казахстан", slug="kz", is_active=True)
    city = City.objects.create(country=country, name="Астана", slug="astana", is_active=True)
    category = ServiceCategory.objects.create(name="Ремонт", slug="remont", is_active=True)
    service = Service.objects.create(category=category, name="Ремонт квартир", slug="remont-kvartir", is_active=True)
    return city, service


def make_imported_company(name="Ремонт Гейт", slug="remont-gate"):
    return Company.objects.create(
        name=name,
        slug=slug,
        short_description="Проверяемый подрядчик по ремонту квартир с публичными источниками.",
        website_url="https://gate.example",
        phone="+77000000000",
        is_active=True,
        index_status=IndexabilityStatus.NOINDEX.value,
        seo_title=f"{name} — досье Otzoviki KZ",
        seo_description="Проверяемый подрядчик по ремонту квартир с публичными источниками.",
        canonical_path=f"/kz/company/{slug}/",
        source_count=0,
        last_verified_at=None,
        methodology_version="",
    )


@pytest.mark.django_db
def test_publish_company_dossiers_promotes_only_companies_that_pass_trust_gate(service_context, tmp_path):
    city, service = service_context
    ready = make_imported_company()
    CompanyService.objects.create(company=ready, city=city, service=service, is_primary=True)
    now = timezone.now()
    ExternalSource.objects.create(company=ready, source_type=ExternalSource.SourceType.YANDEX, name="Яндекс", url="https://yandex.kz/maps/org/gate", same_as_verified=True, captured_at=now)
    ExternalSource.objects.create(company=ready, source_type=ExternalSource.SourceType.TWO_GIS, name="2ГИС", url="https://2gis.kz/astana/firm/gate", same_as_verified=True, captured_at=now)

    weak = make_imported_company(name="Ремонт Слабый", slug="remont-weak")
    CompanyService.objects.create(company=weak, city=city, service=service, is_primary=True)
    ExternalSource.objects.create(company=weak, source_type=ExternalSource.SourceType.YANDEX, name="Яндекс", url="https://yandex.kz/maps/org/weak", same_as_verified=False, captured_at=now)

    out = io.StringIO()
    call_command("publish_company_dossiers", report=str(tmp_path / "publish-report.csv"), stdout=out)

    ready.refresh_from_db()
    weak.refresh_from_db()
    assert ready.index_status == IndexabilityStatus.INDEXABLE
    assert ready.source_count == 2
    assert ready.last_verified_at is not None
    assert ready.methodology_version == "company-dossier-trust-gate-v1"
    assert weak.index_status == IndexabilityStatus.NOINDEX.value
    assert "published=1" in out.getvalue()
    assert "blocked=1" in out.getvalue()


@pytest.mark.django_db
def test_publish_company_dossiers_dry_run_reports_without_mutation(service_context, tmp_path):
    city, service = service_context
    company = make_imported_company()
    CompanyService.objects.create(company=company, city=city, service=service, is_primary=True)
    now = timezone.now()
    ExternalSource.objects.create(company=company, source_type=ExternalSource.SourceType.YANDEX, name="Яндекс", url="https://yandex.kz/maps/org/gate", same_as_verified=True, captured_at=now)
    ExternalSource.objects.create(company=company, source_type=ExternalSource.SourceType.TWO_GIS, name="2ГИС", url="https://2gis.kz/astana/firm/gate", same_as_verified=True, captured_at=now)
    report = tmp_path / "publish-report.csv"

    call_command("publish_company_dossiers", report=str(report), dry_run=True)

    company.refresh_from_db()
    assert company.index_status == IndexabilityStatus.NOINDEX.value
    rows = list(csv.DictReader(io.StringIO(report.read_text())))
    assert rows[0]["status"] == "would_publish"
    assert rows[0]["verified_sources"] == "2"
    assert rows[0]["reason"] == "passes_company_dossier_trust_gate_v1"
