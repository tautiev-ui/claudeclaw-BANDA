import pytest

from apps.editorial.models import Author, MethodologyVersion
from apps.guides.models import (
    Guide,
    GuideCategory,
    GuideChecklistItem,
    GuideFAQ,
    GuideInternalLink,
    GuideRiskItem,
    GuideSourceReference,
)


@pytest.mark.django_db
def test_published_guide_has_canonical_url_author_and_methodology():
    author = Author.objects.create(full_name="Редакция", role=Author.Role.EDITOR, slug="editorial")
    methodology = MethodologyVersion.objects.create(version="2026.1", title="Методология", summary="Как проверяем")
    category = GuideCategory.objects.create(name="Проверка компаний", slug="proverka-kompaniy")
    guide = Guide.objects.create(
        category=category,
        author=author,
        methodology=methodology,
        title="Как проверить ремонтную компанию в Алматы",
        slug="kak-proverit-remontnuyu-kompaniyu",
        summary="Чеклист проверки подрядчика.",
        body="Проверяйте договор, смету, отзывы и следы в Яндексе.",
        status=Guide.Status.PUBLISHED,
    )

    assert guide.get_absolute_url() == "/kz/guides/kak-proverit-remontnuyu-kompaniyu/"
    assert guide.is_public is True
    assert list(Guide.objects.public()) == [guide]
    assert str(guide) == "Как проверить ремонтную компанию в Алматы"


@pytest.mark.django_db
def test_guide_components_are_ordered_and_visible():
    category = GuideCategory.objects.create(name="Договор", slug="dogovor")
    guide = Guide.objects.create(
        category=category,
        title="Договор на ремонт",
        slug="dogovor-na-remont",
        summary="Что проверить",
        body="Body",
        status=Guide.Status.PUBLISHED,
    )
    checklist = GuideChecklistItem.objects.create(guide=guide, position=2, text="Проверьте гарантию")
    risk = GuideRiskItem.objects.create(guide=guide, position=1, risk="Аванс без договора", mitigation="Платить по этапам")
    faq = GuideFAQ.objects.create(guide=guide, position=3, question="Нужен ли акт?", answer="Да, после этапа работ.")

    assert list(guide.checklist_items.all()) == [checklist]
    assert list(guide.risk_items.all()) == [risk]
    assert list(guide.faq_items.all()) == [faq]
    assert str(risk) == "Договор на ремонт · Аванс без договора"


@pytest.mark.django_db
def test_guide_source_and_internal_links_support_money_page_navigation():
    category = GuideCategory.objects.create(name="Отзывы", slug="otzyvy")
    guide = Guide.objects.create(category=category, title="Как читать отзывы", slug="kak-chitat-otzyvy", summary="", body="Body")
    source = GuideSourceReference.objects.create(
        guide=guide,
        label="Правила публикации отзывов",
        url="https://example.com/review-policy",
        source_type=GuideSourceReference.SourceType.POLICY,
    )
    link = GuideInternalLink.objects.create(
        guide=guide,
        label="Рейтинг ремонтных компаний Алматы",
        url="/kz/almaty/reyting-remontnyh-kompaniy/",
        target_type=GuideInternalLink.TargetType.RANKING,
    )

    assert source.is_external is True
    assert link.is_money_page is True
    assert str(link) == "Как читать отзывы → Рейтинг ремонтных компаний Алматы"
