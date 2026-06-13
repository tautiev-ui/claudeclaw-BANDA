import pytest

from apps.business.models import ClaimProfileRequest, ReputationAuditLead
from apps.companies.models import Company


@pytest.mark.django_db
def test_claim_profile_form_shows_paid_profile_disclosure(client):
    response = client.get("/claim-profile/")

    assert response.status_code == 200
    html = response.content.decode()
    assert "платный профиль не влияет на рейтинг" in html.lower()
    assert '<meta name="robots" content="noindex,follow">' in html
    assert "Право на ответ" in html
    assert '<link rel="canonical" href="http://testserver/claim-profile/">' in html
    assert '"@type": "BreadcrumbList"' in html
    assert "Что нужно для проверки" in html
    assert "БИН или документы компании" in html
    assert "Что происходит после заявки" in html
    assert "не даёт права удалять отзывы" in html


@pytest.mark.django_db
def test_claim_profile_form_creates_pending_request_with_consent(client):
    company = Company.objects.create(name="Alma Remont", slug="alma-remont")

    response = client.post(
        "/claim-profile/",
        {
            "company_slug": company.slug,
            "contact_name": "Айдар",
            "contact_email": "owner@example.com",
            "phone": "+77000000000",
            "proof_note": "БИН и документы компании",
            "consent_given": "on",
        },
    )

    assert response.status_code == 302
    claim = ClaimProfileRequest.objects.get(company=company)
    assert claim.status == ClaimProfileRequest.Status.PENDING
    assert claim.source_page == "/claim-profile/"
    assert claim.consent_given is True


@pytest.mark.django_db
def test_reputation_audit_form_is_noindex(client):
    response = client.get("/reputation-audit/")

    assert response.status_code == 200
    html = response.content.decode()
    assert '<meta name="robots" content="noindex,follow">' in html
    assert '<link rel="canonical" href="http://testserver/reputation-audit/">' in html
    assert '"@type": "BreadcrumbList"' in html
    assert "Аудит репутации" in html
    assert "Что проверяем" in html
    assert "Yandex Search" in html
    assert "Алиса и AI answers" in html
    assert "Что вы получите" in html
    assert "Скриншоты и чувствительные доказательства" in html


@pytest.mark.django_db
def test_reputation_audit_form_creates_lead_with_requested_surfaces(client):
    company = Company.objects.create(name="Alma Remont", slug="alma-remont")

    response = client.post(
        "/reputation-audit/",
        {
            "company_slug": company.slug,
            "contact_name": "Айдар",
            "contact_email": "owner@example.com",
            "phone": "+77000000000",
            "requested_surfaces": ["otzoviki", "yandex", "2gis", "google", "ai"],
            "consent_given": "on",
        },
    )

    assert response.status_code == 302
    lead = ReputationAuditLead.objects.get(company=company)
    assert lead.source_page == "/reputation-audit/"
    assert lead.requested_surfaces == ["otzoviki", "yandex", "2gis", "google", "ai"]
    assert lead.has_yandex_ai_scope is True
