import pytest
from django.utils import timezone

from apps.guides.models import (
    Guide,
    GuideCategory,
    GuideChecklistItem,
    GuideFAQ,
    GuideInternalLink,
    GuideRiskItem,
    GuideSourceReference,
)
from apps.seo.indexability import IndexabilityStatus


@pytest.mark.django_db
def test_guide_detail_renders_decision_tool_blocks_and_links(client):
    category = GuideCategory.objects.create(name="Проверка", slug="proverka")
    guide = Guide.objects.create(
        category=category,
        title="Как проверить ремонтную компанию",
        slug="kak-proverit-remontnuyu-kompaniyu",
        summary="Чеклист проверки подрядчика.",
        body="Проверяйте договор, смету, отзывы и внешний след.",
        status=Guide.Status.PUBLISHED,
        index_status=IndexabilityStatus.INDEXABLE,
        seo_title="Как проверить ремонтную компанию",
        seo_description="Чеклист проверки ремонтной компании перед договором.",
        source_count=1,
        last_verified_at=timezone.now(),
        methodology_version="mvp-1",
    )
    GuideChecklistItem.objects.create(guide=guide, position=1, text="Проверить договор")
    GuideRiskItem.objects.create(guide=guide, position=1, risk="Аванс без договора", mitigation="Платить по этапам")
    GuideFAQ.objects.create(guide=guide, position=1, question="Нужен ли акт?", answer="Да, после каждого этапа.")
    GuideSourceReference.objects.create(guide=guide, label="Правила отзывов", url="https://example.com/review-policy", source_type=GuideSourceReference.SourceType.POLICY)
    GuideInternalLink.objects.create(guide=guide, label="Рейтинг ремонтных компаний Алматы", url="/kz/almaty/reyting-remontnyh-kompaniy/", target_type=GuideInternalLink.TargetType.RANKING)

    response = client.get(guide.get_absolute_url())

    assert response.status_code == 200
    html = response.content.decode()
    assert '<meta name="robots" content="index,follow">' in html
    assert '<link rel="canonical" href="http://testserver/kz/guides/kak-proverit-remontnuyu-kompaniyu/">' in html
    assert "BreadcrumbList" in html
    assert "Как проверить ремонтную компанию" in html
    assert "Launch-ready guide" in html
    assert "Editorial QA" in html
    assert "sources: 1" in html
    assert "methodology: mvp-1" in html
    assert "Короткий ответ" in html
    assert "Начните с договора, сметы, отзывов и внешнего следа" in html
    assert "Что проверить до договора" in html
    assert "Проверить договор" in html
    assert "Риски и как снизить" in html
    assert "Аванс без договора" in html
    assert "Платить по этапам" in html
    assert "FAQ по выбору подрядчика" in html
    assert "Нужен ли акт?" in html
    assert "Источники" in html
    assert "Правила отзывов" in html
    assert 'href="https://example.com/review-policy" rel="nofollow noopener noreferrer" target="_blank"' in html
    assert "Внутренние переходы" in html
    assert "/kz/almaty/reyting-remontnyh-kompaniy/" in html
    assert 'href="/kz/almaty/reyting-remontnyh-kompaniy/" rel=' not in html
    assert "/kz/almaty/remont-kvartir/" in html
    assert "/claim-profile/" in html
    assert "/right-of-reply/" in html
    assert "не является юридической консультацией" in html
    assert "Платный профиль не влияет на рейтинг" in html
    assert "Приватные доказательства не публикуются" in html


@pytest.mark.django_db
def test_draft_guide_returns_404(client):
    category = GuideCategory.objects.create(name="Проверка", slug="proverka")
    guide = Guide.objects.create(category=category, title="Draft", slug="draft", summary="", body="Body", status=Guide.Status.DRAFT)

    response = client.get(guide.get_absolute_url())

    assert response.status_code == 404
