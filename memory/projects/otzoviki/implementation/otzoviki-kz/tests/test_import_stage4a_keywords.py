import csv
from pathlib import Path

import pytest
from django.core.management import call_command

from apps.keywords.models import Keyword, KeywordCluster, KeywordPageMap, KeywordURLCompetitorEvidence


@pytest.mark.django_db
def test_import_stage4a_keywords_command_imports_queries_and_evidence(tmp_path):
    queries_path = tmp_path / "strict_target_queries.csv"
    evidence_path = tmp_path / "keyword_url_onpage_join.csv"
    write_csv(
        queries_path,
        ["query_norm", "freq_base_sum", "target_cluster", "suggested_page_type"],
        [
            ["ремонт квартир алматы", "120", "apartment_repair", "geo_service_page"],
            ["ремонт квартир алматы", "120", "apartment_repair", "geo_service_page"],
            ["рейтинг ремонтных компаний", "80", "contractor_reputation", "ranking_or_best_page"],
            ["строительство домов алматы", "60", "house_construction", "service_cluster_or_guide"],
        ],
    )
    write_csv(
        evidence_path,
        ["query_norm", "domain", "url", "position", "freq_base", "target_cluster", "suggested_page_type", "onpage_title", "onpage_h1"],
        [
            ["ремонт квартир алматы", "example.kz", "https://example.kz/remont/", "3", "120", "apartment_repair", "geo_service_page", "Title", "H1"],
        ],
    )

    call_command("import_stage4a_keywords", "--queries", str(queries_path), "--evidence", str(evidence_path))

    assert Keyword.objects.count() == 3
    keyword = Keyword.objects.get(normalized_query="ремонт квартир алматы")
    assert keyword.frequency == 120
    assert keyword.target_cluster == "apartment_repair"
    evidence = KeywordURLCompetitorEvidence.objects.get(keyword=keyword)
    assert evidence.domain == "example.kz"
    assert evidence.position == 3

    cluster = KeywordCluster.objects.get(slug="apartment_repair")
    assert cluster.name == "apartment repair"
    assert cluster.page_type == KeywordPageMap.PageType.CITY_SERVICE
    assert cluster.intent == KeywordCluster.Intent.COMMERCIAL
    assert list(cluster.keywords.order_by("normalized_query")) == [keyword]
    page_map = KeywordPageMap.objects.get(cluster=cluster)
    assert page_map.page_type == KeywordPageMap.PageType.CITY_SERVICE
    assert page_map.canonical_pattern == "/kz/{city}/remont-kvartir/"
    assert page_map.priority == KeywordPageMap.Priority.P0
    assert page_map.is_indexable_candidate is False

    reputation_cluster = KeywordCluster.objects.get(slug="contractor_reputation")
    assert reputation_cluster.page_type == KeywordPageMap.PageType.RANKING
    assert reputation_cluster.page_maps.get().canonical_pattern == "/kz/{city}/reyting-remontnyh-kompaniy/"

    house_cluster = KeywordCluster.objects.get(slug="house_construction")
    assert house_cluster.page_maps.get().canonical_pattern == "/kz/{city}/stroitelstvo-domov/"


def write_csv(path: Path, headers: list[str], rows: list[list[str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)
