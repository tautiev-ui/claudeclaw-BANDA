import csv
import io

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command

from apps.keywords.models import KeywordCluster, KeywordPageMap


@pytest.mark.django_db
def test_seed_markin_next_wave_page_maps_creates_p0_p1_expansion_queue():
    call_command("seed_markin_next_wave_page_maps")

    assert KeywordCluster.objects.filter(slug__startswith="markin-next-").count() >= 10
    page_maps = KeywordPageMap.objects.filter(cluster__slug__startswith="markin-next-")
    assert page_maps.filter(priority=KeywordPageMap.Priority.P0, is_indexable_candidate=True).count() >= 6
    assert page_maps.filter(page_type=KeywordPageMap.PageType.CITY_SERVICE).exists()
    assert page_maps.filter(page_type=KeywordPageMap.PageType.RANKING).exists()
    assert page_maps.filter(page_type=KeywordPageMap.PageType.PRICE).exists()
    assert page_maps.filter(page_type=KeywordPageMap.PageType.GUIDE).exists()
    assert page_maps.filter(page_type=KeywordPageMap.PageType.COMPANY_DOSSIER).exists()
    money_page_maps = page_maps.filter(page_type__in=KeywordPageMap.MONEY_PAGE_TYPES)
    assert all("{city}" in pm.canonical_pattern or "{slug}" in pm.canonical_pattern for pm in money_page_maps)
    assert page_maps.filter(canonical_pattern="/reputation-audit/", is_indexable_candidate=False).exists()


@pytest.mark.django_db
def test_markin_next_wave_export_csv_requires_staff_and_reports_actions(client):
    response = client.get("/admin/keywords/markin-next-wave.csv")
    assert response.status_code == 302
    assert "/admin/login/" in response["Location"]

    call_command("seed_markin_next_wave_page_maps")
    staff = get_user_model().objects.create_user(username="markin-next-wave", password="pass", is_staff=True)
    client.force_login(staff)

    response = client.get("/admin/keywords/markin-next-wave.csv")

    assert response.status_code == 200
    assert response["Content-Type"] == "text/csv; charset=utf-8"
    assert response["Content-Disposition"] == 'attachment; filename="markin-next-wave.csv"'
    rows = list(csv.DictReader(io.StringIO(response.content.decode())))
    assert rows
    assert {"cluster_slug", "page_type", "priority", "canonical_pattern", "indexable_candidate", "next_action", "markin_stage"}.issubset(rows[0].keys())
    assert any(row["priority"] == "P0" and row["indexable_candidate"] == "true" for row in rows)
    assert any(row["page_type"] == "city_service" for row in rows)
    assert any(row["page_type"] == "company_dossier" for row in rows)
