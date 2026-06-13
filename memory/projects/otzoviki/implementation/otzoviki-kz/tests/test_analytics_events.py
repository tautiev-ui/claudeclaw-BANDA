import pytest
from django.test import RequestFactory

from apps.analytics.models import AnalyticsEvent, track_event
from apps.companies.models import Company


@pytest.mark.django_db
def test_company_dossier_open_tracks_analytics_event(client):
    company = Company.objects.create(name="Alma Remont", slug="alma-remont")

    response = client.get(company.get_absolute_url())

    assert response.status_code == 200
    event = AnalyticsEvent.objects.get(event_type=AnalyticsEvent.EventType.COMPANY_DOSSIER_OPEN)
    assert event.path == "/kz/company/alma-remont/"
    assert event.company == company


@pytest.mark.django_db
def test_review_submit_start_and_complete_events_are_tracked(client):
    company = Company.objects.create(name="Alma Remont", slug="alma-remont")

    get_response = client.get(f"/kz/company/{company.slug}/reviews/new/")
    post_response = client.post(
        f"/kz/company/{company.slug}/reviews/new/",
        {
            "author_name": "Клиент",
            "title": "Сделали ремонт",
            "body": "Работы приняли по акту.",
            "quality_rating": "5",
            "timeline_rating": "4",
            "price_rating": "4",
            "communication_rating": "4",
            "warranty_rating": "5",
            "overall_rating": "5",
        },
    )

    assert get_response.status_code == 200
    assert post_response.status_code == 302
    assert AnalyticsEvent.objects.filter(event_type=AnalyticsEvent.EventType.REVIEW_SUBMIT_START, company=company).exists()
    assert AnalyticsEvent.objects.filter(event_type=AnalyticsEvent.EventType.REVIEW_SUBMIT_COMPLETE, company=company).exists()


@pytest.mark.django_db
def test_search_claim_and_audit_submit_events_are_tracked(client):
    company = Company.objects.create(name="Alma Remont", slug="alma-remont")

    client.get("/search/", {"q": "alma"})
    client.post(
        "/claim-profile/",
        {
            "company_slug": company.slug,
            "contact_name": "Айдар",
            "contact_email": "owner@example.com",
            "phone": "+77000000000",
            "proof_note": "Документы",
            "consent_given": "on",
        },
    )
    client.post(
        "/reputation-audit/",
        {
            "company_slug": company.slug,
            "contact_name": "Айдар",
            "contact_email": "owner@example.com",
            "phone": "+77000000000",
            "requested_surfaces": ["otzoviki", "yandex", "ai"],
            "consent_given": "on",
        },
    )

    assert AnalyticsEvent.objects.filter(event_type=AnalyticsEvent.EventType.SEARCH, query="alma").exists()
    assert AnalyticsEvent.objects.filter(event_type=AnalyticsEvent.EventType.CLAIM_PROFILE_SUBMIT, company=company).exists()
    assert AnalyticsEvent.objects.filter(event_type=AnalyticsEvent.EventType.AUDIT_LEAD_SUBMIT, company=company).exists()


@pytest.mark.django_db
def test_track_event_strips_request_query_string_and_redacts_pii_from_query_and_metadata():
    request = RequestFactory().get("/search/?q=alma&email=owner@example.com&phone=77000000000")

    event = track_event(
        event_type=AnalyticsEvent.EventType.SEARCH,
        request=request,
        query="owner@example.com +77000000000 alma remont",
        metadata={
            "contact_email": "owner@example.com",
            "phone": "+77000000000",
            "surface": "search",
            "nested": {"email": "nested@example.com", "safe": "ok"},
        },
    )

    assert event.path == "/search/"
    assert "owner@example.com" not in event.query
    assert "+77000000000" not in event.query
    assert "[email]" in event.query
    assert "[phone]" in event.query
    assert event.metadata["contact_email"] == "[redacted]"
    assert event.metadata["phone"] == "[redacted]"
    assert event.metadata["surface"] == "search"
    assert event.metadata["nested"] == {"email": "[redacted]", "safe": "ok"}
