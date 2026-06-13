import pytest
from django.utils import timezone

from apps.companies.models import Company, CompanyService
from apps.locations.models import City, Country
from apps.seo.indexability import IndexabilityStatus
from apps.services.models import Service, ServiceCategory


def make_city_service():
    kz = Country.objects.create(code="kz", name="Казахстан", slug="kz", is_active=True)
    city = City.objects.create(country=kz, name="Алматы", slug="almaty", is_active=True)
    category = ServiceCategory.objects.create(name="Ремонт", slug="remont", is_active=True)
    service = Service.objects.create(category=category, name="Ремонт квартир", slug="remont-kvartir", is_active=True)
    return city, service


@pytest.mark.django_db
def test_company_canonical_profile_status_and_trust_gate():
    company = Company.objects.create(
        name="Remont Pro Almaty",
        slug="remont-pro-almaty",
        profile_status=Company.ProfileStatus.VERIFIED,
        index_status=IndexabilityStatus.INDEXABLE,
        seo_title="Remont Pro Almaty отзывы",
        seo_description="Досье ремонтной компании Remont Pro Almaty",
        source_count=4,
        last_verified_at=timezone.now(),
        methodology_version="v1",
    )

    assert str(company) == "Remont Pro Almaty"
    assert company.get_absolute_url() == "/kz/company/remont-pro-almaty/"
    assert company.profile_status_label == "verified"
    assert company.get_indexability_decision(require_trust_data=True).allowed is True
    assert company.schema_eligible is True


@pytest.mark.django_db
def test_company_empty_profile_stays_noindex():
    company = Company.objects.create(name="Empty Company", slug="empty-company")

    assert company.get_absolute_url() == "/kz/company/empty-company/"
    assert company.robots_meta == "noindex,follow"
    assert company.schema_eligible is False


@pytest.mark.django_db
def test_company_service_links_company_to_city_and_service():
    city, service = make_city_service()
    company = Company.objects.create(name="Alma Remont", slug="alma-remont")
    link = CompanyService.objects.create(company=company, city=city, service=service, is_primary=True)

    assert str(link) == "Alma Remont · Ремонт квартир · Алматы"
    assert link.service_page_url == "/kz/almaty/remont-kvartir/"
    assert link.company_url == "/kz/company/alma-remont/"


@pytest.mark.django_db
def test_company_service_uniqueness_for_company_city_service():
    city, service = make_city_service()
    company = Company.objects.create(name="Alma Remont", slug="alma-remont")
    CompanyService.objects.create(company=company, city=city, service=service)

    with pytest.raises(Exception):
        CompanyService.objects.create(company=company, city=city, service=service)
