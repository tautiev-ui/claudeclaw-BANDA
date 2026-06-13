import pytest
from django.utils import timezone

from apps.guides.models import Guide, GuideCategory
from apps.seo.indexability import IndexabilityStatus


def create_published_guide(title="Как проверить ремонтную компанию", slug="kak-proverit-remontnuyu-kompaniyu"):
    category = GuideCategory.objects.create(name="Проверка компании", slug="proverka", description="Как проверить подрядчика")
    return Guide.objects.create(
        category=category,
        title=title,
        slug=slug,
        summary="Чеклист проверки перед договором.",
        body="Проверяйте отзывы, смету, договор и официальный ответ.",
        status=Guide.Status.PUBLISHED,
        index_status=IndexabilityStatus.INDEXABLE,
        seo_title=title,
        seo_description="Гайд Otzoviki KZ по проверке подрядчика.",
        source_count=1,
        last_verified_at=timezone.now(),
        methodology_version="mvp-1",
    )


@pytest.mark.django_db
def test_guides_hub_renders_published_guides_categories_and_money_ctas(client):
    guide = create_published_guide()
    Guide.objects.create(
        category=guide.category,
        title="Черновик",
        slug="draft-guide",
        summary="Draft",
        body="Draft body",
        status=Guide.Status.DRAFT,
    )

    response = client.get("/kz/guides/")

    assert response.status_code == 200
    html = response.content.decode()
    assert '<meta name="robots" content="index,follow">' in html
    assert '<link rel="canonical" href="http://testserver/kz/guides/">' in html
    assert '"@type": "BreadcrumbList"' in html
    assert "Гайды Otzoviki KZ" in html
    assert "Проверка компании" in html
    assert "Как проверить ремонтную компанию" in html
    assert "/kz/guides/kak-proverit-remontnuyu-kompaniyu/" in html
    assert "Черновик" not in html
    assert "/kz/almaty/remont-kvartir/" in html
    assert "/claim-profile/" in html


@pytest.mark.django_db
def test_guides_hub_empty_state_is_noindex(client):
    response = client.get("/kz/guides/")

    assert response.status_code == 200
    html = response.content.decode()
    assert '<meta name="robots" content="noindex,follow">' in html
    assert "Гайды скоро будут добавлены" in html


@pytest.mark.django_db
def test_for_business_page_has_trust_disclosure_and_b2b_links(client):
    response = client.get("/for-business/")

    assert response.status_code == 200
    html = response.content.decode()
    assert '<meta name="robots" content="index,follow">' in html
    assert '<link rel="canonical" href="http://testserver/for-business/">' in html
    assert '"@type": "BreadcrumbList"' in html
    assert "Для бизнеса" in html
    assert "платный профиль не влияет" in html.lower()
    assert "/claim-profile/" in html
    assert "/reputation-audit/" in html
    assert "/right-of-reply/" in html
    assert "QR" in html
    assert "Что получает бизнес" in html
    assert "Верифицированный представитель" in html
    assert "Репутационный аудит Yandex/AI" in html
    assert "Безопасные границы" in html
    assert "Публичное раскрытие" in html
    assert "Следующие шаги" in html
