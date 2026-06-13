import pytest

from apps.keywords.models import Keyword, KeywordCluster, KeywordPageMap, KeywordURLCompetitorEvidence


@pytest.mark.django_db
def test_keyword_stores_stage4a_source_metadata_and_normalized_query():
    keyword = Keyword.objects.create(
        query=" Ремонт квартир Алматы ",
        frequency=120,
        source=Keyword.Source.KEYS_SO,
        region="kz",
        target_cluster="city_service_remont_kvartir",
    )

    assert keyword.normalized_query == "ремонт квартир алматы"
    assert keyword.source == Keyword.Source.KEYS_SO
    assert str(keyword) == "ремонт квартир алматы · 120"


@pytest.mark.django_db
def test_competitor_evidence_connects_keyword_to_url_and_onpage_signals():
    keyword = Keyword.objects.create(query="ремонт квартир алматы", frequency=120)
    evidence = KeywordURLCompetitorEvidence.objects.create(
        keyword=keyword,
        url="https://example.kz/remont-kvartir-almaty/",
        domain="example.kz",
        title="Ремонт квартир в Алматы",
        h1="Ремонт квартир",
        position=3,
    )

    assert evidence.domain == "example.kz"
    assert evidence.is_top_10 is True
    assert str(evidence) == "ремонт квартир алматы → example.kz · #3"


@pytest.mark.django_db
def test_keyword_cluster_and_page_map_define_target_template():
    cluster = KeywordCluster.objects.create(
        slug="city-service-remont-kvartir",
        name="City service: ремонт квартир",
        intent=KeywordCluster.Intent.COMMERCIAL,
        page_type=KeywordPageMap.PageType.CITY_SERVICE,
    )
    keyword = Keyword.objects.create(query="ремонт квартир алматы", frequency=120, target_cluster=cluster.slug)
    cluster.keywords.add(keyword)
    page_map = KeywordPageMap.objects.create(
        cluster=cluster,
        page_type=KeywordPageMap.PageType.CITY_SERVICE,
        canonical_pattern="/kz/{city}/remont-kvartir/",
        priority=KeywordPageMap.Priority.P0,
        is_indexable_candidate=True,
    )

    assert page_map.canonical_for(city="almaty") == "/kz/almaty/remont-kvartir/"
    assert page_map.is_money_page is True
    assert list(cluster.keywords.all()) == [keyword]
