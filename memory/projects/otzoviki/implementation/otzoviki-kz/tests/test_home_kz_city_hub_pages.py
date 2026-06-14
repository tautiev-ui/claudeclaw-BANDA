import pytest
from django.utils import timezone

from apps.companies.models import Company, CompanyService
from apps.guides.models import Guide, GuideCategory
from apps.locations.models import City, Country
from apps.reviews.models import RatingSnapshot
from apps.services.models import Service, ServiceCategory
from apps.seo.indexability import IndexabilityStatus


def seed_local_mvp():
    country = Country.objects.create(code="KZ", name="Казахстан", slug="kz")
    almaty = City.objects.create(country=country, name="Алматы", slug="almaty")
    astana = City.objects.create(country=country, name="Астана", slug="astana")
    category = ServiceCategory.objects.create(name="Ремонт", slug="remont")
    service = Service.objects.create(category=category, name="Ремонт квартир", slug="remont-kvartir")
    company = Company.objects.create(
        name="Alma Remont",
        slug="alma-remont",
        short_description="Ремонт квартир под ключ в Алматы",
        index_status=IndexabilityStatus.INDEXABLE,
        seo_title="Alma Remont — отзывы",
        seo_description="Отзывы и досье Alma Remont",
        source_count=2,
        last_verified_at=timezone.now(),
        methodology_version="mvp-1",
    )
    CompanyService.objects.create(company=company, city=almaty, service=service, is_primary=True)
    RatingSnapshot.objects.create(company=company, review_count=3, average_rating=4.6, quality_rating=4.7, timeline_rating=4.3, communication_rating=4.8)
    guide_category = GuideCategory.objects.create(name="Проверка компании", slug="proverka")
    guide = Guide.objects.create(
        category=guide_category,
        title="Как проверить ремонтную компанию",
        slug="kak-proverit-remontnuyu-kompaniyu",
        summary="Короткий чеклист перед договором.",
        body="Проверяйте отзывы, смету и официальный ответ.",
        status=Guide.Status.PUBLISHED,
        index_status=IndexabilityStatus.INDEXABLE,
        seo_title="Как проверить ремонтную компанию",
        seo_description="Чеклист проверки ремонтной компании",
        source_count=1,
        last_verified_at=timezone.now(),
        methodology_version="mvp-1",
    )
    return country, almaty, astana, service, company, guide


@pytest.mark.django_db
def test_homepage_lists_live_cities_companies_and_guides(client):
    seed_local_mvp()

    response = client.get("/")

    assert response.status_code == 200
    html = response.content.decode()
    assert '<meta name="robots" content="index,follow">' in html
    assert '<link rel="canonical" href="http://testserver/">' in html
    assert "Алматы" in html
    assert "Alma Remont" in html
    assert "Как проверить ремонтную компанию" in html
    assert "Launch batch" not in html
    assert "Otzoviki KZ MVP" not in html
    assert "SEO-first SSR" not in html
    assert "50–100" not in html
    assert "открытием индексации" not in html
    assert "Введите название компании или услугу" in html
    assert "Проверьте ремонтную компанию до оплаты" in html
    assert "Проверенные досье" in html
    assert "Как пользоваться" in html
    assert "Запросите смету только после проверки" in html


@pytest.mark.django_db
def test_kz_root_lists_cities_services_and_trust_links(client):
    seed_local_mvp()

    response = client.get("/kz/")

    assert response.status_code == 200
    html = response.content.decode()
    assert '<meta name="robots" content="index,follow">' in html
    assert '<link rel="canonical" href="http://testserver/kz/">' in html
    assert '"@type": "BreadcrumbList"' in html
    assert "Казахстан" in html
    assert "Алматы" in html
    assert "Астана" in html
    assert "Ремонт квартир" in html
    assert "/kz/almaty/remont-kvartir/" in html
    assert "/methodology/" in html
    assert "Что можно проверить" in html
    assert "Выберите город и услугу" in html
    assert "/review-policy/" in html
    assert "/right-of-reply/" in html
    assert "Как считается рейтинг" in html
    assert "Яндекс, 2ГИС и Google" in html


@pytest.mark.django_db
def test_city_hub_renders_local_service_links_and_is_indexable_only_with_data(client):
    seed_local_mvp()

    response = client.get("/kz/almaty/")

    assert response.status_code == 200
    html = response.content.decode()
    assert '<meta name="robots" content="index,follow">' in html
    assert '<link rel="canonical" href="http://testserver/kz/almaty/">' in html
    assert '"@type": "BreadcrumbList"' in html
    assert "Алматы" in html
    assert "Alma Remont" in html
    assert "/kz/almaty/remont-kvartir/" in html
    assert "/kz/almaty/reyting-remontnyh-kompaniy/" in html
    assert "/kz/almaty/remont-kvartir/ceny/" in html
    assert "Городская матрица выбора" in html
    assert "Отзывы, официальный ответ и внешний след" in html
    assert "Частые вопросы по компаниям в Алматы" in html
    assert "Платный профиль не влияет на рейтинг" in html
    assert "/right-of-reply/" in html


@pytest.mark.django_db
def test_city_hub_empty_city_is_noindex(client):
    seed_local_mvp()

    response = client.get("/kz/astana/")

    assert response.status_code == 200
    html = response.content.decode()
    assert '<meta name="robots" content="noindex,follow">' in html
    assert "Недостаточно данных для индексации города" in html
