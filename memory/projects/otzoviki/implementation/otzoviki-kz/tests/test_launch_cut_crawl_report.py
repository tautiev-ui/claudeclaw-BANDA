import csv
import io

import pytest
from django.core.management import call_command
from django.contrib.auth import get_user_model

from apps.launchqa.models import IndexingMonitorURL


@pytest.mark.django_db
def test_run_launch_cut_crawl_records_indexability_monitor_rows(client):
    call_command("seed_launch_cut_content")
    call_command("run_launch_cut_crawl")

    required = {
        "/": "public_indexable",
        "/kz/": "public_indexable",
        "/kz/astana/": "public_indexable",
        "/kz/astana/remont-kvartir/": "public_indexable",
        "/kz/guides/kak-proverit-remontnuyu-kompaniyu/": "public_indexable",
        "/claim-profile/": "public_noindex",
        "/search/": "public_noindex",
        "/business/dashboard/": "private_noindex",
    }
    for url, page_type in required.items():
        row = IndexingMonitorURL.objects.get(url=url)
        assert row.page_type == page_type
        assert row.http_status in {200, 302}
        assert row.index_status in {IndexingMonitorURL.IndexStatus.DISCOVERED, IndexingMonitorURL.IndexStatus.NOINDEX}
        assert row.has_launch_risk is False
    assert IndexingMonitorURL.objects.filter(index_status=IndexingMonitorURL.IndexStatus.ERROR).count() == 0


@pytest.mark.django_db
def test_launch_crawl_report_csv_requires_staff_and_has_no_failures(client):
    anonymous = client.get("/admin/launch-qa/launch-crawl-report.csv")
    assert anonymous.status_code == 302
    assert "/admin/login/" in anonymous["Location"]

    call_command("seed_launch_cut_content")
    call_command("run_launch_cut_crawl")
    staff = get_user_model().objects.create_user(username="crawl-report", password="pass", is_staff=True)
    client.force_login(staff)

    response = client.get("/admin/launch-qa/launch-crawl-report.csv")

    assert response.status_code == 200
    assert response["Content-Type"] == "text/csv; charset=utf-8"
    assert response["Content-Disposition"] == 'attachment; filename="launch-crawl-report.csv"'
    rows = list(csv.DictReader(io.StringIO(response.content.decode())))
    assert rows
    assert {"url", "page_type", "http_status", "robots_meta", "status", "notes"}.issubset(rows[0].keys())
    assert all(row["status"] == "pass" for row in rows)
    assert any(row["url"] == "/kz/astana/" and row["robots_meta"] == "index,follow" for row in rows)
    assert any(row["url"] == "/claim-profile/" and row["robots_meta"] == "noindex,follow" for row in rows)
