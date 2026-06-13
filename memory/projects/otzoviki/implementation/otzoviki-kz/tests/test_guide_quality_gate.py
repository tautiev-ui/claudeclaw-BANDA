import pytest

from apps.guides.models import (
    Guide,
    GuideCategory,
    GuideChecklistItem,
    GuideFAQ,
    GuideInternalLink,
    GuideRiskItem,
    GuideSourceReference,
)


def create_published_guide(**kwargs):
    category = kwargs.pop("category", None) or GuideCategory.objects.create(name="Проверка", slug="proverka")
    defaults = {
        "category": category,
        "title": "Как проверить ремонтную компанию",
        "slug": "kak-proverit-remontnuyu-kompaniyu",
        "summary": "Практический чеклист проверки подрядчика перед договором.",
        "body": "Проверяйте договор, смету, гарантию, публичные отзывы и внешний след компании перед оплатой.",
        "status": Guide.Status.PUBLISHED,
    }
    defaults.update(kwargs)
    return Guide.objects.create(**defaults)


@pytest.mark.django_db
def test_guide_quality_gate_requires_sources_money_links_and_decision_blocks():
    guide = create_published_guide()

    assert not guide.is_launch_ready
    assert "missing_source_reference" in guide.quality_issues
    assert "missing_money_page_link" in guide.quality_issues
    assert "missing_checklist" in guide.quality_issues
    assert "missing_risk_mitigation" in guide.quality_issues
    assert "missing_faq" in guide.quality_issues

    GuideSourceReference.objects.create(guide=guide, label="Правила отзывов", url="https://example.com/review-policy")
    GuideInternalLink.objects.create(guide=guide, label="Рейтинг Алматы", url="/kz/almaty/reyting-remontnyh-kompaniy/", target_type=GuideInternalLink.TargetType.RANKING)
    GuideChecklistItem.objects.create(guide=guide, text="Проверить договор")
    GuideRiskItem.objects.create(guide=guide, risk="Аванс без договора", mitigation="Платить по этапам")
    GuideFAQ.objects.create(guide=guide, question="Нужен ли акт?", answer="Да, после этапа.")

    assert guide.quality_issues == []
    assert guide.is_launch_ready


@pytest.mark.django_db
def test_guide_quality_gate_flags_generic_ai_filler_phrases():
    guide = create_published_guide(
        body="В современном мире ремонт квартир является важной задачей. В данной статье мы рассмотрим основные аспекты выбора компании.",
    )
    GuideSourceReference.objects.create(guide=guide, label="Источник", url="https://example.com/source")
    GuideInternalLink.objects.create(guide=guide, label="Рейтинг Алматы", url="/kz/almaty/reyting-remontnyh-kompaniy/", target_type=GuideInternalLink.TargetType.RANKING)
    GuideChecklistItem.objects.create(guide=guide, text="Проверить договор")
    GuideRiskItem.objects.create(guide=guide, risk="Аванс", mitigation="Этапная оплата")
    GuideFAQ.objects.create(guide=guide, question="Нужен ли акт?", answer="Да")

    assert "generic_ai_filler" in guide.quality_issues
    assert not guide.is_launch_ready


@pytest.mark.django_db
def test_guide_detail_for_non_launch_ready_guide_is_noindex(client):
    guide = create_published_guide()

    response = client.get(guide.get_absolute_url())

    assert response.status_code == 200
    html = response.content.decode()
    assert '<meta name="robots" content="noindex,follow">' in html
    assert "Content quality gate" in html
