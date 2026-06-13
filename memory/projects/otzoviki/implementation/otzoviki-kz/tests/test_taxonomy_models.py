import pytest

from apps.locations.models import City, Country
from apps.services.models import Service, ServiceCategory


@pytest.mark.django_db
def test_country_and_city_public_paths():
    kz = Country.objects.create(code="kz", name="Казахстан", slug="kz", is_active=True)
    city = City.objects.create(country=kz, name="Алматы", slug="almaty", region="Алматинская область", is_active=True)

    assert str(kz) == "Казахстан"
    assert kz.get_absolute_url() == "/kz/"
    assert str(city) == "Алматы"
    assert city.get_absolute_url() == "/kz/almaty/"
    assert city.public_label == "Алматы, Казахстан"


@pytest.mark.django_db
def test_active_city_queryset_filters_inactive_country_and_city():
    kz = Country.objects.create(code="kz", name="Казахстан", slug="kz", is_active=True)
    inactive_country = Country.objects.create(code="ru", name="Россия", slug="ru", is_active=False)
    active = City.objects.create(country=kz, name="Астана", slug="astana", is_active=True)
    City.objects.create(country=kz, name="Черновик", slug="draft-city", is_active=False)
    City.objects.create(country=inactive_country, name="СПб", slug="spb", is_active=True)

    assert list(City.objects.active()) == [active]


@pytest.mark.django_db
def test_service_category_and_service_paths_for_city():
    kz = Country.objects.create(code="kz", name="Казахстан", slug="kz", is_active=True)
    city = City.objects.create(country=kz, name="Алматы", slug="almaty", is_active=True)
    category = ServiceCategory.objects.create(name="Ремонт", slug="remont", is_active=True)
    service = Service.objects.create(category=category, name="Ремонт квартир", slug="remont-kvartir", is_active=True)

    assert str(category) == "Ремонт"
    assert str(service) == "Ремонт квартир"
    assert service.get_absolute_url(city) == "/kz/almaty/remont-kvartir/"
    assert service.ranking_url(city) == "/kz/almaty/reyting-remontnyh-kompaniy/"
    assert service.price_url(city) == "/kz/almaty/remont-kvartir/ceny/"
    assert service.public_label(city) == "Ремонт квартир в Алматы"


@pytest.mark.django_db
def test_active_service_queryset_filters_inactive_category_and_service():
    active_category = ServiceCategory.objects.create(name="Ремонт", slug="remont", is_active=True)
    inactive_category = ServiceCategory.objects.create(name="Черновик", slug="draft", is_active=False)
    active = Service.objects.create(category=active_category, name="Ремонт квартир", slug="remont-kvartir", is_active=True)
    Service.objects.create(category=active_category, name="Неактивная", slug="inactive", is_active=False)
    Service.objects.create(category=inactive_category, name="Скрытая", slug="hidden", is_active=True)

    assert list(Service.objects.active()) == [active]
