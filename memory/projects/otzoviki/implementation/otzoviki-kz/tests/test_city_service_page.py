import pytest
from django.utils import timezone

from apps.companies.models import Company, CompanyService
from apps.locations.models import City, Country
from apps.reviews.models import RatingSnapshot
from apps.services.models import Service, ServiceCategory


@pytest.mark.django_db
def test_city_service_page_renders_company_cards_and_indexable_when_has_data(client):
    country = Country.objects.create(code="KZ", name="Казахстан", slug="kz")
    city = City.objects.create(country=country, name="Алматы", slug="almaty")
    category = ServiceCategory.objects.create(name="Ремонт", slug="remont")
    service = Service.objects.create(category=category, name="Ремонт квартир", slug="remont-kvartir")
    company = Company.objects.create(name="Alma Remont", slug="alma-remont", short_description="Ремонт квартир под ключ")
    CompanyService.objects.create(company=company, city=city, service=service, is_primary=True)
    RatingSnapshot.objects.create(company=company, review_count=3, average_rating=4.6, quality_rating=4.7, timeline_rating=4.3, communication_rating=4.8)

    response = client.get("/kz/almaty/remont-kvartir/")

    assert response.status_code == 200
    html = response.content.decode()
    assert '<meta name="robots" content="index,follow">' in html
    assert "Ремонт квартир в Алматы" in html
    assert "Alma Remont" in html
    assert "4.6" in html
    assert '<link rel="canonical" href="http://testserver/kz/almaty/remont-kvartir/">' in html
    assert '"@type": "BreadcrumbList"' in html
    assert "/methodology/" in html
    assert "/kz/almaty/reyting-remontnyh-kompaniy/" in html
    assert "Что проверить перед выбором подрядчика" in html
    assert "договор и смета" in html
    assert "Публичная методология и право на ответ" in html
    assert "Частые вопросы по услуге в Алматы" in html
    assert "Как сравнивать компании по услуге Ремонт квартир?" in html
    assert "Цены являются ориентиром" in html
    assert "Платный профиль не влияет на рейтинг" in html
    assert "Фильтры выбора подрядчика" in html
    assert "город + услуга" in html
    assert "Сравнительная таблица компаний" in html
    assert "Яндекс/2ГИС/Google след" in html
    assert "Ориентиры цен и сметы" in html
    assert "Черновая отделка" in html
    assert "Как выбрать подрядчика" in html
    assert "Собрать shortlist" in html
    assert "Красные флаги" in html


@pytest.mark.django_db
def test_city_service_page_empty_state_is_noindex(client):
    country = Country.objects.create(code="KZ", name="Казахстан", slug="kz")
    City.objects.create(country=country, name="Алматы", slug="almaty")
    category = ServiceCategory.objects.create(name="Ремонт", slug="remont")
    Service.objects.create(category=category, name="Ремонт квартир", slug="remont-kvartir")

    response = client.get("/kz/almaty/remont-kvartir/")

    assert response.status_code == 200
    html = response.content.decode()
    assert '<meta name="robots" content="noindex,follow">' in html
    assert "Недостаточно данных для индексации" in html
