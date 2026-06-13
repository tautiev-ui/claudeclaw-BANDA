import json

import pytest
from django.test import RequestFactory
from django.utils import timezone

from apps.companies.models import Company
from apps.reviews.models import Review
from apps.seo.indexability import IndexabilityStatus
from apps.seo.schema import build_company_schema, build_site_schema


@pytest.mark.django_db
def test_site_schema_contains_website_organization_and_search_action():
    request = RequestFactory().get("/")

    schema = build_site_schema(request)

    assert schema["@context"] == "https://schema.org"
    assert {node["@type"] for node in schema["@graph"]} == {"Organization", "WebSite"}
    website = next(node for node in schema["@graph"] if node["@type"] == "WebSite")
    assert website["url"] == "http://testserver/"
    assert website["potentialAction"]["@type"] == "SearchAction"
    json.dumps(schema, ensure_ascii=False)


@pytest.mark.django_db
def test_company_schema_uses_only_visible_owned_reviews_for_aggregate_rating():
    request = RequestFactory().get("/kz/company/alma-remont/")
    company = Company.objects.create(
        name="Alma Remont",
        slug="alma-remont",
        website_url="https://alma.example.kz/",
        index_status=IndexabilityStatus.INDEXABLE,
        seo_title="Alma Remont отзывы",
        seo_description="Досье Alma Remont",
        source_count=2,
        last_verified_at=timezone.now(),
        methodology_version="2026.1",
    )
    Review.objects.create(company=company, author_name="A", title="Good", body="Body", status=Review.Status.APPROVED, quality_rating=5, timeline_rating=4, communication_rating=4)
    Review.objects.create(company=company, author_name="B", title="Pending", body="Body", status=Review.Status.PENDING, quality_rating=1, timeline_rating=1, communication_rating=1)

    schema = build_company_schema(request, company)

    assert schema["@type"] == "HomeAndConstructionBusiness"
    assert schema["name"] == "Alma Remont"
    assert schema["url"] == "http://testserver/kz/company/alma-remont/"
    assert schema["sameAs"] == ["https://alma.example.kz/"]
    assert schema["aggregateRating"]["ratingValue"] == 4.3
    assert schema["aggregateRating"]["reviewCount"] == 1
    assert len(schema["review"]) == 1
    assert schema["review"][0]["name"] == "Good"
    json.dumps(schema, ensure_ascii=False)


@pytest.mark.django_db
def test_company_schema_returns_none_when_trust_gates_fail():
    request = RequestFactory().get("/kz/company/empty/")
    company = Company.objects.create(name="Empty", slug="empty", index_status=IndexabilityStatus.DRAFT)

    assert build_company_schema(request, company) is None
