import pytest
from django.contrib.auth import get_user_model

from apps.keywords.models import Keyword, KeywordCluster, KeywordPageMap, KeywordURLCompetitorEvidence


@pytest.mark.django_db
def test_keyword_admin_report_requires_staff_login(client):
    response = client.get("/admin/keywords/report/")

    assert response.status_code == 302
    assert "/admin/login/" in response["Location"]


@pytest.mark.django_db
def test_keyword_admin_report_shows_counts_top_queries_page_maps_and_unmapped(client):
    staff = get_user_model().objects.create_user(username="seo", password="pass", is_staff=True)
    client.force_login(staff)
    mapped_keyword = Keyword.objects.create(query="ремонт квартир алматы", frequency=120, target_cluster="city-service")
    Keyword.objects.create(query="отзывы о компании алма ремонт", frequency=90, target_cluster="company-dossier")
    Keyword.objects.create(query="неразобранный запрос", frequency=80, target_cluster="")
    cluster = KeywordCluster.objects.create(slug="city-service", name="City service", intent=KeywordCluster.Intent.COMMERCIAL, page_type="city_service")
    cluster.keywords.add(mapped_keyword)
    KeywordURLCompetitorEvidence.objects.create(keyword=mapped_keyword, domain="example.kz", url="https://example.kz/remont/", position=3)
    KeywordPageMap.objects.create(cluster=cluster, page_type=KeywordPageMap.PageType.CITY_SERVICE, canonical_pattern="/kz/{city}/remont-kvartir/", priority=KeywordPageMap.Priority.P0, is_indexable_candidate=True)

    response = client.get("/admin/keywords/report/")

    assert response.status_code == 200
    html = response.content.decode()
    assert '<meta name="robots" content="noindex,follow">' in html
    assert "Keyword/page mapping report" in html
    assert "Всего keywords" in html
    assert "Evidence rows" in html
    assert "3" in html
    assert "ремонт квартир алматы" in html
    assert "неразобранный запрос" in html
    assert "city_service" in html
    assert "demand: 120" in html
    assert "Launch risk: unmapped high-frequency demand" in html
    assert "Top evidence domains" in html
    assert "example.kz · rows: 1 · top-10: 1" in html
    assert "/kz/{city}/remont-kvartir/" in html
    assert "Unmapped" in html


@pytest.mark.django_db
def test_keyword_page_map_export_requires_staff_login(client):
    response = client.get("/admin/keywords/page-map-export.csv")

    assert response.status_code == 302
    assert "/admin/login/" in response["Location"]


@pytest.mark.django_db
def test_keyword_page_map_export_contains_markin_mapping_fields(client):
    staff = get_user_model().objects.create_user(username="seo-export", password="pass", is_staff=True)
    client.force_login(staff)
    keyword = Keyword.objects.create(query="ремонт квартир алматы", frequency=120, target_cluster="city-service")
    cluster = KeywordCluster.objects.create(slug="city-service", name="City service", intent=KeywordCluster.Intent.COMMERCIAL, page_type="city_service")
    cluster.keywords.add(keyword)
    KeywordURLCompetitorEvidence.objects.create(keyword=keyword, domain="example.kz", url="https://example.kz/remont/", position=3)
    KeywordPageMap.objects.create(cluster=cluster, page_type=KeywordPageMap.PageType.CITY_SERVICE, canonical_pattern="/kz/{city}/remont-kvartir/", priority=KeywordPageMap.Priority.P0, is_indexable_candidate=False)

    response = client.get("/admin/keywords/page-map-export.csv")

    assert response.status_code == 200
    assert response["Content-Type"] == "text/csv"
    body = response.content.decode()
    assert "cluster_slug,page_type,canonical_pattern,priority,is_indexable_candidate,keyword_count,frequency_sum,evidence_count" in body
    assert "city-service,city_service,/kz/{city}/remont-kvartir/,P0,False,1,120,1" in body
