import csv
import io

import pytest
from django.contrib.auth import get_user_model

from apps.launchqa.models import IndexingMonitorURL


@pytest.mark.django_db
def test_seo_audit_export_requires_staff(client):
    response = client.get("/admin/launch-qa/seo-audit-export.csv")

    assert response.status_code == 302
    assert "/admin/login/" in response["Location"]


@pytest.mark.django_db
def test_seo_audit_export_returns_csv_with_indexing_monitor_rows(client):
    IndexingMonitorURL.objects.create(
        url="/kz/company/empty/",
        page_type="company",
        index_status=IndexingMonitorURL.IndexStatus.NOINDEX,
        http_status=200,
        is_empty_profile=True,
        notes="empty dossier should stay closed",
    )
    staff = get_user_model().objects.create_user(username="exporter", password="pass", is_staff=True)
    client.force_login(staff)

    response = client.get("/admin/launch-qa/seo-audit-export.csv")

    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/csv")
    assert "attachment" in response["Content-Disposition"]
    content = response.content.decode()
    rows = list(csv.DictReader(io.StringIO(content)))
    assert rows[0]["url"] == "/kz/company/empty/"
    assert rows[0]["page_type"] == "company"
    assert rows[0]["index_status"] == IndexingMonitorURL.IndexStatus.NOINDEX
    assert rows[0]["http_status"] == "200"
    assert rows[0]["is_empty_profile"] == "True"
    assert rows[0]["has_launch_risk"] == "False"
    assert rows[0]["notes"] == "empty dossier should stay closed"


@pytest.mark.django_db
def test_seo_audit_export_flags_empty_indexed_profiles_as_launch_risk(client):
    IndexingMonitorURL.objects.create(
        url="/kz/company/thin/",
        page_type="company",
        index_status=IndexingMonitorURL.IndexStatus.INDEXED,
        http_status=200,
        is_empty_profile=True,
    )
    staff = get_user_model().objects.create_user(username="risk", password="pass", is_staff=True)
    client.force_login(staff)

    response = client.get("/admin/launch-qa/seo-audit-export.csv")

    rows = list(csv.DictReader(io.StringIO(response.content.decode())))
    assert rows[0]["has_launch_risk"] == "True"


@pytest.mark.django_db
def test_seo_audit_export_flags_submitted_or_indexed_error_urls_as_launch_risk(client):
    IndexingMonitorURL.objects.create(
        url="/kz/company/missing/",
        page_type="company",
        index_status=IndexingMonitorURL.IndexStatus.SUBMITTED,
        http_status=404,
        is_empty_profile=False,
    )
    staff = get_user_model().objects.create_user(username="risk404", password="pass", is_staff=True)
    client.force_login(staff)

    response = client.get("/admin/launch-qa/seo-audit-export.csv")

    rows = list(csv.DictReader(io.StringIO(response.content.decode())))
    assert rows[0]["has_launch_risk"] == "True"
