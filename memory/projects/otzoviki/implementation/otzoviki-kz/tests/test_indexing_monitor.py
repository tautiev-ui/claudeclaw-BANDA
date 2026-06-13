import pytest
from django.contrib.auth import get_user_model


@pytest.mark.django_db
def test_indexing_monitor_requires_staff(client):
    response = client.get("/admin/launch-qa/indexing-monitor/")

    assert response.status_code == 302
    assert "/admin/login/" in response["Location"]


@pytest.mark.django_db
def test_indexing_monitor_shows_submitted_indexed_noindex_and_empty_profile_counts(client):
    from apps.launchqa.models import IndexingMonitorURL

    IndexingMonitorURL.objects.create(url="/", page_type="home", index_status=IndexingMonitorURL.IndexStatus.INDEXED, http_status=200)
    IndexingMonitorURL.objects.create(url="/kz/company/empty/", page_type="company", index_status=IndexingMonitorURL.IndexStatus.NOINDEX, http_status=200, is_empty_profile=True)
    IndexingMonitorURL.objects.create(url="/kz/almaty/", page_type="city", index_status=IndexingMonitorURL.IndexStatus.SUBMITTED, http_status=200)

    staff = get_user_model().objects.create_user(username="indexer", password="pass", is_staff=True)
    client.force_login(staff)

    response = client.get("/admin/launch-qa/indexing-monitor/")

    assert response.status_code == 200
    html = response.content.decode()
    assert '<meta name="robots" content="noindex,follow">' in html
    assert "Indexing monitor" in html
    assert "Submitted" in html
    assert "Indexed" in html
    assert "Noindex" in html
    assert "Empty profiles" in html
    assert "/kz/company/empty/" in html
    assert "1" in html
    assert "40-gate indexing readiness" in html
    assert "Submitted URLs" in html
    assert "Indexed URLs" in html
    assert "Noindex inventory" in html
    assert "Empty profile suppression" in html
    assert "HTTP error risk" in html
    assert "Submitted but 404" in html
    assert "Indexed empty profile" in html
    assert "Export SEO audit CSV" in html
    assert "/admin/launch-qa/seo-audit-export.csv" in html


@pytest.mark.django_db
def test_indexing_monitor_url_flags_launch_risk_for_empty_indexed_profile():
    from apps.launchqa.models import IndexingMonitorURL

    row = IndexingMonitorURL.objects.create(
        url="/kz/company/thin/",
        page_type="company",
        index_status=IndexingMonitorURL.IndexStatus.INDEXED,
        http_status=200,
        is_empty_profile=True,
    )

    assert row.has_launch_risk

    row.index_status = IndexingMonitorURL.IndexStatus.NOINDEX
    row.save(update_fields=["index_status"])

    assert not row.has_launch_risk


@pytest.mark.django_db
def test_indexing_monitor_flags_submitted_404_as_launch_risk(client):
    from apps.launchqa.models import IndexingMonitorURL

    IndexingMonitorURL.objects.create(
        url="/kz/company/missing/",
        page_type="company",
        index_status=IndexingMonitorURL.IndexStatus.SUBMITTED,
        http_status=404,
        is_empty_profile=False,
    )
    staff = get_user_model().objects.create_user(username="riskdash", password="pass", is_staff=True)
    client.force_login(staff)

    response = client.get("/admin/launch-qa/indexing-monitor/")
    html = response.content.decode()

    assert response.status_code == 200
    assert "Launch risks: 1" in html
    assert "/kz/company/missing/" in html
    assert "HTTP: 404" in html
    assert "Launch risk" in html
