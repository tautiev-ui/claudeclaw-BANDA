import pytest

from apps.business.models import ClaimProfileRequest, OfficialResponse, ReputationAuditLead
from apps.companies.models import Company


@pytest.mark.django_db
def test_claim_profile_submission_captures_safe_internal_referer_as_source_page(client):
    company = Company.objects.create(name="Alma Remont", slug="alma-remont")

    response = client.post(
        "/claim-profile/",
        {
            "company_slug": company.slug,
            "contact_name": "Owner",
            "contact_email": "owner@example.com",
            "phone": "+77000000000",
            "proof_note": "BIN proof",
            "consent_given": "on",
        },
        HTTP_REFERER="http://testserver/kz/company/alma-remont/",
    )

    assert response.status_code == 302
    claim = ClaimProfileRequest.objects.get()
    assert claim.source_page == "/kz/company/alma-remont/"


@pytest.mark.django_db
def test_reputation_audit_submission_rejects_external_referer_for_source_page(client):
    company = Company.objects.create(name="Alma Remont", slug="alma-remont")

    response = client.post(
        "/reputation-audit/",
        {
            "company_slug": company.slug,
            "contact_name": "Owner",
            "contact_email": "owner@example.com",
            "phone": "+77000000000",
            "requested_surfaces": ["yandex", "ai"],
            "consent_given": "on",
        },
        HTTP_REFERER="https://evil.example/path",
    )

    assert response.status_code == 302
    lead = ReputationAuditLead.objects.get()
    assert lead.source_page == "/reputation-audit/"


@pytest.mark.django_db
def test_official_response_submission_captures_safe_internal_referer_as_source_page(client):
    company = Company.objects.create(name="Alma Remont", slug="alma-remont")

    response = client.post(
        f"/kz/company/{company.slug}/official-response/new/",
        {
            "contact_name": "Owner",
            "contact_email": "owner@example.com",
            "role_title": "Директор",
            "body": "Готовы предоставить документы.",
        },
        HTTP_REFERER="http://testserver/kz/company/alma-remont/?from=reply-cta",
    )

    assert response.status_code == 302
    official_response = OfficialResponse.objects.get()
    assert official_response.source_page == "/kz/company/alma-remont/"
