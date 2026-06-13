import pytest

from apps.business.models import (
    BusinessAccount,
    BusinessRepresentative,
    ClaimProfileRequest,
    OfficialResponse,
    ReputationAuditLead,
)
from apps.companies.models import Company


@pytest.mark.django_db
def test_claim_profile_request_defaults_to_pending_and_can_mark_company_claimed():
    company = Company.objects.create(name="Alma Remont", slug="alma-remont")
    request = ClaimProfileRequest.objects.create(
        company=company,
        contact_name="Айдар",
        contact_email="owner@example.com",
        phone="+77000000000",
        proof_note="БИН и договор аренды офиса",
        source_page="/claim-profile/",
        consent_given=True,
    )

    assert request.status == ClaimProfileRequest.Status.PENDING
    assert request.consent_given is True
    assert str(request) == "Alma Remont · Айдар · pending"

    request.approve()
    company.refresh_from_db()
    request.refresh_from_db()

    assert request.status == ClaimProfileRequest.Status.APPROVED
    assert company.profile_status == Company.ProfileStatus.CLAIMED


@pytest.mark.django_db
def test_business_representative_is_verified_only_when_approved_and_email_verified():
    company = Company.objects.create(name="Alma Remont", slug="alma-remont")
    account = BusinessAccount.objects.create(company=company, display_name="Alma Remont Business")
    representative = BusinessRepresentative.objects.create(
        account=account,
        full_name="Айдар",
        email="owner@example.com",
        role_title="Директор",
        verification_status=BusinessRepresentative.VerificationStatus.APPROVED,
        email_verified=True,
    )

    assert account.company == company
    assert representative.is_verified is True
    assert str(representative) == "Айдар · Alma Remont Business"


@pytest.mark.django_db
def test_official_response_public_queryset_only_returns_published_responses():
    company = Company.objects.create(name="Alma Remont", slug="alma-remont")
    account = BusinessAccount.objects.create(company=company, display_name="Alma Remont Business")
    representative = BusinessRepresentative.objects.create(
        account=account,
        full_name="Айдар",
        email="owner@example.com",
    )
    published = OfficialResponse.objects.create(
        company=company,
        representative=representative,
        body="Готовы предоставить акты и гарантийные документы.",
        status=OfficialResponse.Status.PUBLISHED,
        source_page="/kz/company/alma-remont/",
    )
    OfficialResponse.objects.create(
        company=company,
        representative=representative,
        body="Черновик ответа.",
        status=OfficialResponse.Status.PENDING,
    )

    assert list(OfficialResponse.objects.public()) == [published]
    assert published.is_public is True
    assert published.right_of_reply_policy_url == "/right-of-reply/"


@pytest.mark.django_db
def test_reputation_audit_lead_stores_requested_surfaces_and_consent():
    company = Company.objects.create(name="Alma Remont", slug="alma-remont")
    lead = ReputationAuditLead.objects.create(
        company=company,
        contact_name="Айдар",
        contact_email="owner@example.com",
        phone="+77000000000",
        source_page="/reputation-audit/",
        requested_surfaces=["otzoviki", "yandex", "2gis", "google", "ai"],
        consent_given=True,
    )

    assert lead.status == ReputationAuditLead.Status.NEW
    assert lead.has_yandex_ai_scope is True
    assert lead.consent_given is True
    assert str(lead) == "Alma Remont · owner@example.com · new"
