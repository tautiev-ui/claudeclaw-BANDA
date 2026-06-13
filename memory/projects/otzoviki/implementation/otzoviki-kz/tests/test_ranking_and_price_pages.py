import pytest
from django.utils import timezone

from apps.companies.models import Company, CompanyService
from apps.locations.models import City, Country
from apps.reviews.models import RatingSnapshot
from apps.services.models import Service, ServiceCategory
from apps.seo.indexability import IndexabilityStatus


def create_city_service():
    country = Country.objects.create(code="KZ", name="Казахстан", slug="kz")
    city = City.objects.create(country=country, name="Алматы", slug="almaty")
    category = ServiceCategory.objects.create(name="Ремонт", slug="remont")
    service = Service.objects.create(category=category, name="Ремонт квартир", slug="remont-kvartir")
    return city, service


def create_indexable_company(name: str, slug: str):
    return Company.objects.create(
        name=name,
        slug=slug,
        short_description=f"{name}: ремонт квартир",
        index_status=IndexabilityStatus.INDEXABLE,
        seo_title=f"{name} — отзывы",
        seo_description=f"Отзывы и досье {name}",
        source_count=2,
        last_verified_at=timezone.now(),
        methodology_version="mvp-1",
    )


@pytest.mark.django_db
def test_ranking_page_sorts_companies_by_rating_and_is_indexable(client):
    city, service = create_city_service()
    best = create_indexable_company("Best Remont", "best-remont")
    second = create_indexable_company("Second Remont", "second-remont")
    CompanyService.objects.create(company=second, city=city, service=service)
    CompanyService.objects.create(company=best, city=city, service=service)
    RatingSnapshot.objects.create(company=second, review_count=7, average_rating=4.2, quality_rating=4.3, timeline_rating=4.1, communication_rating=4.2)
    RatingSnapshot.objects.create(company=best, review_count=11, average_rating=4.8, quality_rating=4.9, timeline_rating=4.7, communication_rating=4.8)

    response = client.get("/kz/almaty/reyting-remontnyh-kompaniy/")

    assert response.status_code == 200
    html = response.content.decode()
    assert '<meta name="robots" content="index,follow">' in html
    assert "Рейтинг ремонтных компаний в Алматы" in html
    assert html.index("Best Remont") < html.index("Second Remont")
    assert "4.8" in html
    assert '<link rel="canonical" href="http://testserver/kz/almaty/reyting-remontnyh-kompaniy/">' in html
    assert '"@type": "BreadcrumbList"' in html
    assert "методология" in html.lower()
    assert "платный профиль не влияет" in html.lower()
    assert "Факторы рейтинга" in html
    assert "количество и свежесть отзывов" in html
    assert "официальные ответы компаний" in html
    assert "Компания может заявить профиль или дать ответ" in html
    assert "Частые вопросы о рейтинге в Алматы" in html
    assert "Почему компания выше в рейтинге?" in html
    assert "/kz/almaty/remont-kvartir/" in html


@pytest.mark.django_db
def test_ranking_page_empty_state_is_noindex(client):
    create_city_service()

    response = client.get("/kz/almaty/reyting-remontnyh-kompaniy/")

    assert response.status_code == 200
    html = response.content.decode()
    assert '<meta name="robots" content="noindex,follow">' in html
    assert "Недостаточно данных для рейтинга" in html


@pytest.mark.django_db
def test_price_page_renders_service_context_and_noindex_until_data(client):
    city, service = create_city_service()
    company = create_indexable_company("Alma Remont", "alma-remont")
    CompanyService.objects.create(company=company, city=city, service=service)

    response = client.get("/kz/almaty/remont-kvartir/ceny/")

    assert response.status_code == 200
    html = response.content.decode()
    assert '<meta name="robots" content="index,follow">' in html
    assert '<link rel="canonical" href="http://testserver/kz/almaty/remont-kvartir/ceny/">' in html
    assert '"@type": "BreadcrumbList"' in html
    assert "Цены на ремонт квартир в Алматы" in html
    assert "Alma Remont" in html
    assert "не является публичной офертой" in html
    assert "проверяйте смету" in html.lower()
    assert "Ориентиры и ограничения" in html
    assert "этапы оплаты" in html
    assert "Риски в смете" in html
    assert "скрытые работы" in html
    assert "Частые вопросы о ценах в Алматы" in html
    assert "Как понять, что смета занижена?" in html
    assert "/kz/almaty/remont-kvartir/" in html
    assert "/kz/almaty/reyting-remontnyh-kompaniy/" in html


@pytest.mark.django_db
def test_price_page_empty_state_is_noindex(client):
    create_city_service()

    response = client.get("/kz/almaty/remont-kvartir/ceny/")

    assert response.status_code == 200
    html = response.content.decode()
    assert '<meta name="robots" content="noindex,follow">' in html
    assert "Недостаточно данных для ценовой страницы" in html
