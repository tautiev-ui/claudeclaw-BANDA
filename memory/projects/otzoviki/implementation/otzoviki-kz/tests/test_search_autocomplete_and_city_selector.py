import pytest

from apps.companies.models import Company
from apps.guides.models import Guide, GuideCategory
from apps.keywords.models import Keyword
from apps.locations.models import City, Country
from apps.services.models import Service, ServiceCategory


@pytest.mark.django_db
def test_search_autocomplete_returns_typed_company_city_service_guide_and_keyword_results(client):
    country = Country.objects.create(code="KZ", name="Казахстан", slug="kz")
    city = City.objects.create(country=country, name="Алматы", slug="almaty")
    category = ServiceCategory.objects.create(name="Ремонт", slug="remont")
    Service.objects.create(category=category, name="Ремонт квартир", slug="remont-kvartir")
    Company.objects.create(name="Alma Remont", slug="alma-remont")
    guide_category = GuideCategory.objects.create(name="Проверка", slug="proverka")
    Guide.objects.create(category=guide_category, title="Как проверить ремонтную компанию", slug="kak-proverit-remontnuyu-kompaniyu", summary="", body="Body", status=Guide.Status.PUBLISHED)
    Keyword.objects.create(query="ремонт квартир алматы", frequency=120)

    response = client.get("/search/autocomplete/", {"q": "ремонт алматы"})

    assert response.status_code == 200
    assert response["Content-Type"] == "application/json"
    payload = response.json()
    assert payload["query"] == "ремонт алматы"
    result_types = {item["type"] for item in payload["results"]}
    assert {"city", "service", "guide", "keyword"}.issubset(result_types)
    urls = {item["url"] for item in payload["results"] if item.get("url")}
    assert "/kz/almaty/" in urls
    assert "/kz/almaty/remont-kvartir/" in urls
    assert "/kz/guides/kak-proverit-remontnuyu-kompaniyu/" in urls


@pytest.mark.django_db
def test_search_autocomplete_short_or_empty_query_returns_empty_results(client):
    response = client.get("/search/autocomplete/", {"q": "р"})

    assert response.status_code == 200
    assert response.json()["results"] == []


@pytest.mark.django_db
def test_global_city_selector_renders_active_cities_and_context_links(client):
    country = Country.objects.create(code="KZ", name="Казахстан", slug="kz")
    City.objects.create(country=country, name="Алматы", slug="almaty")
    City.objects.create(country=country, name="Астана", slug="astana")
    City.objects.create(country=country, name="Скрытый", slug="hidden", is_active=False)

    response = client.get("/kz/almaty/reyting-remontnyh-kompaniy/")

    assert response.status_code == 200
    html = response.content.decode()
    assert 'data-city-selector="true"' in html
    assert "Алматы" in html
    assert "Астана" in html
    assert "Скрытый" not in html
    assert "/kz/astana/remont-kvartir/" in html
    assert "/kz/astana/reyting-remontnyh-kompaniy/" in html
    assert "/kz/astana/remont-kvartir/ceny/" in html
