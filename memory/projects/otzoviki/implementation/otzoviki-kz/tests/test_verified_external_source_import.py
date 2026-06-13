import csv
import io

import pytest
from django.core.management import call_command
from django.utils import timezone

from apps.companies.models import Company
from apps.evidence.models import ExternalSource
from apps.seo.indexability import IndexabilityStatus


@pytest.mark.django_db
def test_import_verified_external_sources_marks_existing_sources_verified(tmp_path):
    company = Company.objects.create(
        name="Эксперт Ремонта",
        slug="ekspert-remonta",
        website_url="https://expertremonta.kz",
        phone="+77770007074",
        short_description="Проверяемая ремонтная компания Алматы.",
        index_status=IndexabilityStatus.NOINDEX.value,
        seo_title="Эксперт Ремонта — досье Otzoviki KZ",
        seo_description="Проверяемая ремонтная компания Алматы.",
        canonical_path="/kz/company/ekspert-remonta/",
    )
    captured_at = timezone.now() - timezone.timedelta(days=3)
    ExternalSource.objects.create(
        company=company,
        source_type=ExternalSource.SourceType.YANDEX,
        name="Яндекс Бизнес",
        url="https://yandex.ru/maps/org/83284830941",
        same_as_verified=False,
        captured_at=captured_at,
    )
    csv_path = tmp_path / "verified.csv"
    csv_path.write_text(
        "name,city_slug,service_slug,website_url,phone,yandex_url,two_gis_url,short_description\n"
        "Эксперт Ремонта,almaty,remont-kvartir,https://expertremonta.kz,+77770007074,https://yandex.ru/maps/org/83284830941/,https://2gis.kz/almaty/firm/70000001081518376,Verified candidate\n"
    )
    report_path = tmp_path / "report.csv"

    out = io.StringIO()
    call_command("import_verified_external_sources", str(csv_path), report=str(report_path), stdout=out)

    assert "processed=1" in out.getvalue()
    assert company.external_sources.filter(source_type=ExternalSource.SourceType.YANDEX, same_as_verified=True).count() == 1
    assert company.external_sources.filter(source_type=ExternalSource.SourceType.TWO_GIS, same_as_verified=True).count() == 1
    rows = list(csv.DictReader(report_path.open()))
    assert rows == [
        {
            "row_number": "2",
            "name": "Эксперт Ремонта",
            "company_id": str(company.pk),
            "slug": "ekspert-remonta",
            "status": "updated",
            "reason": "verified_sources_attached",
            "sources_verified": "2",
        }
    ]


@pytest.mark.django_db
def test_import_verified_external_sources_dry_run_does_not_mutate(tmp_path):
    Company.objects.create(
        name="Idal Concept",
        slug="idal-concept",
        website_url="https://idal.kz",
        short_description="Проверяемая дизайн-студия.",
        index_status=IndexabilityStatus.NOINDEX.value,
    )
    csv_path = tmp_path / "verified.csv"
    csv_path.write_text(
        "name,city_slug,service_slug,website_url,phone,yandex_url,two_gis_url,short_description\n"
        "Idal Concept,almaty,remont-kvartir,https://idal.kz,+77010703103,https://yandex.ru/maps/org/149896655588/,https://2gis.kz/almaty/firm/70000001035552899,Verified candidate\n"
    )
    report_path = tmp_path / "dry.csv"

    call_command("import_verified_external_sources", str(csv_path), report=str(report_path), dry_run=True)

    assert ExternalSource.objects.count() == 0
    row = next(csv.DictReader(report_path.open()))
    assert row["status"] == "dry_run"
    assert row["reason"] == "would_attach_verified_sources"
    assert row["sources_verified"] == "2"
