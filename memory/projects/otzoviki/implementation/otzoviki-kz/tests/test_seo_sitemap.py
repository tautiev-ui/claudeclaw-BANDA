import pytest
from django.utils import timezone

from apps.companies.models import Company, CompanyService
from apps.editorial.models import MethodologyVersion
from apps.guides.models import (
    Guide,
    GuideCategory,
    GuideChecklistItem,
    GuideFAQ,
    GuideInternalLink,
    GuideRiskItem,
    GuideSourceReference,
)
from apps.qr.models import QRReviewFlow
from apps.seo.indexability import IndexabilityStatus
from apps.locations.models import City, Country
from apps.services.models import Service, ServiceCategory


@pytest.mark.django_db
def test_sitemap_includes_only_indexable_public_canonical_urls(client):
    indexable_company = Company.objects.create(
        name="Alma Remont",
        slug="alma-remont",
        index_status=IndexabilityStatus.INDEXABLE,
        seo_title="Alma Remont отзывы",
        seo_description="Досье Alma Remont",
        source_count=2,
        last_verified_at=timezone.now(),
        methodology_version="2026.1",
    )
    Company.objects.create(
        name="Empty Company",
        slug="empty-company",
        index_status=IndexabilityStatus.DRAFT,
        seo_title="Empty",
        seo_description="Empty",
    )
    methodology = MethodologyVersion.objects.create(version="2026.1", title="Методология", summary="Как проверяем")
    category = GuideCategory.objects.create(name="Проверка", slug="proverka")
    indexable_guide = Guide.objects.create(
        category=category,
        methodology=methodology,
        title="Как проверить компанию",
        slug="kak-proverit-kompaniyu",
        summary="Практический гайд",
        body="Body",
        status=Guide.Status.PUBLISHED,
        index_status=IndexabilityStatus.INDEXABLE,
        seo_title="Как проверить компанию",
        seo_description="Гайд по проверке",
        source_count=1,
        last_verified_at=timezone.now(),
        methodology_version="2026.1",
    )
    GuideSourceReference.objects.create(guide=indexable_guide, label="Источник", url="https://example.com/source")
    GuideInternalLink.objects.create(guide=indexable_guide, label="Рейтинг", url="/kz/almaty/reyting-remontnyh-kompaniy/", target_type=GuideInternalLink.TargetType.RANKING)
    GuideChecklistItem.objects.create(guide=indexable_guide, text="Проверить договор")
    GuideRiskItem.objects.create(guide=indexable_guide, risk="Аванс", mitigation="Платить по этапам")
    GuideFAQ.objects.create(guide=indexable_guide, question="Нужен ли акт?", answer="Да")
    low_quality_guide = Guide.objects.create(
        category=category,
        methodology=methodology,
        title="Generic filler guide",
        slug="generic-filler-guide",
        summary="",
        body="В современном мире ремонт является важной задачей.",
        status=Guide.Status.PUBLISHED,
        index_status=IndexabilityStatus.INDEXABLE,
        seo_title="Generic filler guide",
        seo_description="Generic filler",
        source_count=1,
        last_verified_at=timezone.now(),
        methodology_version="2026.1",
    )
    flow = QRReviewFlow.objects.create(company=indexable_company, label="QR")

    response = client.get("/sitemap.xml")

    assert response.status_code == 200
    assert response["Content-Type"].startswith("application/xml")
    xml = response.content.decode()
    assert xml.startswith('<?xml version="1.0" encoding="UTF-8"?>')
    assert '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' in xml
    assert "http://testserver/" in xml
    assert "http://testserver/kz/" in xml
    assert "http://testserver/for-business/" in xml
    assert "http://testserver/methodology/" in xml
    assert "http://testserver/review-policy/" in xml
    assert "http://testserver/right-of-reply/" in xml
    assert f"http://testserver{indexable_company.get_absolute_url()}" in xml
    assert f"http://testserver{indexable_guide.get_absolute_url()}" in xml
    assert "http://testserver/privacy/" in xml
    assert "http://testserver/terms/" in xml
    assert "http://testserver/llms.txt" in xml
    assert "http://testserver/ai-reputation.md" in xml
    assert xml.count("<loc>http://testserver/privacy/</loc>") == 1
    assert "http://testserver/kz/company/empty-company/" not in xml
    assert f"http://testserver{low_quality_guide.get_absolute_url()}" not in xml
    assert f"http://testserver{flow.get_absolute_url()}" not in xml
    assert "http://testserver/search/" not in xml
    assert "http://testserver/business/" not in xml
    assert "http://testserver/business/dashboard/" not in xml
    assert "http://testserver/claim-profile/" not in xml
    assert "http://testserver/reputation-audit/" not in xml
    assert "http://testserver/admin/ai-evidence/capture/" not in xml
    assert f"http://testserver{indexable_company.get_absolute_url()}reviews/new/" not in xml
    assert f"http://testserver{indexable_company.get_absolute_url()}official-response/new/" not in xml


@pytest.mark.django_db
def test_sitemap_includes_populated_markin_city_service_page_maps_only(client):
    country = Country.objects.create(code="KZ", name="Казахстан", slug="kz")
    city = City.objects.create(country=country, name="Алматы", slug="almaty")
    category = ServiceCategory.objects.create(name="Markin clusters", slug="markin-clusters")
    service_slugs = [
        "remont-kvartir",
        "stroitelstvo-domov",
        "dizayn-interera",
        "novostroyki",
        "santehnik",
    ]
    company = Company.objects.create(name="Cluster Company", slug="cluster-company")
    for slug in service_slugs:
        service = Service.objects.create(category=category, name=slug.replace("-", " ").title(), slug=slug)
        CompanyService.objects.create(company=company, city=city, service=service)
    empty_service = Service.objects.create(category=category, name="Пустая услуга", slug="pustaya-usluga")

    response = client.get("/sitemap.xml")

    assert response.status_code == 200
    xml = response.content.decode()
    for slug in service_slugs:
        assert f"http://testserver/kz/almaty/{slug}/" in xml
    assert "http://testserver/kz/almaty/pustaya-usluga/" not in xml


@pytest.mark.django_db
def test_robots_txt_blocks_private_search_qr_and_points_to_sitemap(client):
    response = client.get("/robots.txt")

    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/plain")
    body = response.content.decode()
    assert body.startswith("User-agent: *")
    assert "Allow: /llms.txt" in body
    assert "Allow: /ai-reputation.md" in body
    assert "Allow: /methodology/" in body
    assert "Disallow: /admin/launch-qa/" in body
    assert "Disallow: /admin/keywords/" in body
    assert "Disallow: /admin/ai-evidence/" in body
    assert "Disallow: /admin/" in body
    assert "Disallow: /business/" in body
    assert "Disallow: /search/" in body
    assert "Disallow: /r/" in body
    assert "Sitemap: http://testserver/sitemap.xml" in body
    assert "Crawl-delay" not in body
