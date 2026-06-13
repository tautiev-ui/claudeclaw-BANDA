import pytest

from apps.ai_evidence.models import AIYandexEvidenceLog
from apps.companies.models import Company


@pytest.mark.django_db
def test_ai_yandex_evidence_log_stores_query_region_platform_and_visibility():
    company = Company.objects.create(name="Alma Remont", slug="alma-remont")
    log = AIYandexEvidenceLog.objects.create(
        company=company,
        platform=AIYandexEvidenceLog.Platform.YANDEX_NEURO,
        query="Alma Remont отзывы",
        region="Алматы",
        answer_excerpt="Компания упоминается в отзывах и картах.",
        cited_sources=["https://yandex.kz/maps/org/example/", "https://2gis.kz/almaty/firm/example"],
        sentiment=AIYandexEvidenceLog.Sentiment.MIXED,
        visibility=AIYandexEvidenceLog.Visibility.PUBLIC,
    )

    assert log.is_public_safe is True
    assert log.has_yandex_surface is True
    assert str(log) == "Alma Remont · yandex_neuro · Alma Remont отзывы · Алматы"


@pytest.mark.django_db
def test_private_ai_evidence_is_excluded_from_public_queryset():
    company = Company.objects.create(name="Alma Remont", slug="alma-remont")
    public_log = AIYandexEvidenceLog.objects.create(company=company, platform=AIYandexEvidenceLog.Platform.YANDEX_SEARCH, query="alma отзывы", region="KZ", visibility=AIYandexEvidenceLog.Visibility.PUBLIC)
    AIYandexEvidenceLog.objects.create(company=company, platform=AIYandexEvidenceLog.Platform.AI_OVERVIEW, query="alma жалобы", region="KZ", visibility=AIYandexEvidenceLog.Visibility.PRIVATE)

    assert list(AIYandexEvidenceLog.objects.public()) == [public_log]
