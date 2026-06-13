import pytest

from apps.companies.models import Company
from apps.guides.models import Guide, GuideCategory
from apps.locations.models import City, Country
from apps.search.models import SearchQuery
from apps.services.models import Service, ServiceCategory


@pytest.mark.django_db
def test_search_routes_company_and_records_noindex_query(client):
    Company.objects.create(name="Alma Remont", slug="alma-remont")

    response = client.get("/search/", {"q": "alma"})

    assert response.status_code == 200
    html = response.content.decode()
    assert '<meta name="robots" content="noindex,follow">' in html
    assert "/kz/company/alma-remont/" in html
    assert SearchQuery.objects.get(normalized_query="alma").result_count == 1


@pytest.mark.django_db
def test_search_routes_city_service_and_guide_results(client):
    country = Country.objects.create(code="KZ", name="Казахстан", slug="kz")
    city = City.objects.create(country=country, name="Алматы", slug="almaty")
    category = ServiceCategory.objects.create(name="Ремонт", slug="remont")
    Service.objects.create(category=category, name="Ремонт квартир", slug="remont-kvartir")
    guide_category = GuideCategory.objects.create(name="Проверка", slug="proverka")
    Guide.objects.create(category=guide_category, title="Как проверить компанию", slug="kak-proverit-kompaniyu", summary="", body="Body", status=Guide.Status.PUBLISHED)

    response = client.get("/search/", {"q": "ремонт квартир алматы"})

    assert response.status_code == 200
    html = response.content.decode()
    assert "/kz/almaty/remont-kvartir/" in html
    assert "/kz/almaty/" in html

    guide_response = client.get("/search/", {"q": "проверить компанию"})
    assert "/kz/guides/kak-proverit-kompaniyu/" in guide_response.content.decode()


@pytest.mark.django_db
def test_empty_search_state_is_noindex_and_suggests_submission(client):
    response = client.get("/search/", {"q": "неизвестная компания"})

    assert response.status_code == 200
    html = response.content.decode()
    assert '<meta name="robots" content="noindex,follow">' in html
    assert "Предложить компанию" in html
    assert SearchQuery.objects.get(normalized_query="неизвестная компания").result_count == 0
