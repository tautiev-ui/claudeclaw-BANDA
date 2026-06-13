import csv
import io
from pathlib import Path

import pytest
from django.core.management import call_command

from apps.companies.models import Company, CompanyService
from apps.evidence.models import ExternalSource


@pytest.mark.django_db
def test_import_company_dossiers_creates_draft_noindex_companies_and_validation_report(tmp_path):
    csv_path = tmp_path / "companies.csv"
    csv_path.write_text(
        "name,city_slug,service_slug,website_url,phone,yandex_url,two_gis_url,short_description\n"
        "Ремонт Плюс,astana,remont-kvartir,https://remont-plus.example,+77010000001,https://yandex.kz/maps/org/remont-plus/,https://2gis.kz/astana/firm/remont-plus,Проверяемый подрядчик по ремонту квартир.\n"
        "Ремонт Плюс дубль,astana,remont-kvartir,https://remont-plus.example,+77010000002,https://yandex.kz/maps/org/remont-plus-duplicate/,,Дубль по сайту.\n"
        "Смета Дом,almaty,remont-kvartir,https://smeta-dom.example,+77010000003,https://yandex.kz/maps/org/smeta-dom/,,Компания со сметами и отзывами.\n"
    )
    report_path = tmp_path / "report.csv"

    call_command("import_company_dossiers", str(csv_path), report=str(report_path))

    assert Company.objects.filter(slug="remont-plus").exists()
    assert Company.objects.filter(slug="smeta-dom").exists()
    assert Company.objects.count() == 2
    company = Company.objects.get(slug="remont-plus")
    assert company.index_status == "noindex"
    assert company.source_count == 0
    assert company.methodology_version == ""
    assert company.service_links.filter(city__slug="astana", service__slug="remont-kvartir").exists()
    assert company.external_sources.filter(source_type=ExternalSource.SourceType.YANDEX, same_as_verified=False).exists()
    assert company.external_sources.filter(source_type=ExternalSource.SourceType.TWO_GIS, same_as_verified=False).exists()

    rows = list(csv.DictReader(io.StringIO(report_path.read_text())))
    assert len(rows) == 3
    statuses = [row["status"] for row in rows]
    assert statuses.count("created") == 2
    assert statuses.count("duplicate") == 1
    duplicate = next(row for row in rows if row["status"] == "duplicate")
    assert duplicate["reason"] == "duplicate_website_url"


@pytest.mark.django_db
def test_company_import_template_exists_and_contains_required_headers():
    template = Path("docs/company-import-template.csv")
    assert template.exists()
    headers = template.read_text().splitlines()[0].split(",")
    assert headers == [
        "name",
        "city_slug",
        "service_slug",
        "website_url",
        "phone",
        "yandex_url",
        "two_gis_url",
        "short_description",
    ]


@pytest.mark.django_db
def test_import_company_dossiers_dry_run_writes_report_without_database_mutation(tmp_path):
    csv_path = tmp_path / "companies.csv"
    report_path = tmp_path / "dry-run-report.csv"
    csv_path.write_text(
        "name,city_slug,service_slug,website_url,phone,yandex_url,two_gis_url,short_description\n"
        "Ремонт Тест,astana,remont-kvartir,https://dry.example,+77000000003,https://yandex.kz/maps/org/dry,https://2gis.kz/astana/firm/dry,Тестовая компания\n"
    )

    call_command("import_company_dossiers", str(csv_path), report=str(report_path), dry_run=True)

    rows = list(csv.DictReader(io.StringIO(report_path.read_text())))
    assert rows[0]["status"] == "dry_run"
    assert rows[0]["reason"] == "would_create_draft_noindex"
    assert rows[0]["company_id"] == ""
    assert Company.objects.filter(name="Ремонт Тест").count() == 0
