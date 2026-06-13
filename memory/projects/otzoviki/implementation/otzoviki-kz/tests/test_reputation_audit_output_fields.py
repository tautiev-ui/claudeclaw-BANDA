import pytest

from apps.business.models import ReputationAuditLead
from apps.companies.models import Company


@pytest.mark.django_db
def test_reputation_audit_lead_stores_yandex_ai_output_fields():
    company = Company.objects.create(name="Alma Remont", slug="alma-remont")

    lead = ReputationAuditLead.objects.create(
        company=company,
        contact_name="Айдар",
        contact_email="owner@example.com",
        requested_surfaces=["yandex", "ai"],
        consent_given=True,
        yandex_visibility_summary="Yandex Maps рейтинг 3.8, есть негатив по срокам.",
        ai_visibility_summary="Yandex Neuro цитирует 2GIS и Otzoviki.",
        audit_recommendations="Ответить на негатив, обновить карточку, собрать свежие отзывы.",
    )

    assert lead.has_yandex_ai_scope
    assert lead.has_audit_output
    assert "Yandex Maps" in lead.audit_output_text
    assert "Yandex Neuro" in lead.audit_output_text
    assert "свежие отзывы" in lead.audit_output_text


@pytest.mark.django_db
def test_reputation_audit_form_keeps_output_fields_empty_for_public_lead_submission(client):
    company = Company.objects.create(name="Alma Remont", slug="alma-remont")

    response = client.post(
        "/reputation-audit/",
        {
            "company_slug": company.slug,
            "contact_name": "Айдар",
            "contact_email": "owner@example.com",
            "requested_surfaces": ["yandex", "ai"],
            "consent_given": "on",
        },
    )

    assert response.status_code == 302
    lead = ReputationAuditLead.objects.get(company=company)
    assert lead.yandex_visibility_summary == ""
    assert lead.ai_visibility_summary == ""
    assert lead.audit_recommendations == ""
    assert not lead.has_audit_output
