import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import RequestFactory

from apps.business.admin import ClaimProfileModerationLogAdmin, ClaimProfileModerationLogInline, ClaimProfileRequestAdmin
from apps.business.models import ClaimProfileModerationLog, ClaimProfileRequest
from apps.companies.models import Company


def create_claim_request(status=ClaimProfileRequest.Status.PENDING, slug="alma-remont"):
    company = Company.objects.create(name=f"Alma Remont {slug}", slug=slug)
    return ClaimProfileRequest.objects.create(
        company=company,
        contact_name="Owner",
        contact_email=f"owner-{slug}@example.com",
        phone="+77000000000",
        proof_note="Учредительные документы и договор аренды офиса.",
        source_page=company.get_absolute_url(),
        consent_given=True,
        status=status,
    )


@pytest.mark.django_db
def test_claim_profile_admin_actions_approve_reject_and_log():
    user = get_user_model().objects.create_superuser(username="moderator", password="pass", email="m@example.com")
    request = RequestFactory().post("/admin/business/claimprofilerequest/")
    request.user = user
    model_admin = ClaimProfileRequestAdmin(ClaimProfileRequest, AdminSite())

    approve_request = create_claim_request(slug="approve-claim")
    reject_request = create_claim_request(slug="reject-claim")

    model_admin.mark_approved(request, ClaimProfileRequest.objects.filter(id=approve_request.id))
    model_admin.mark_rejected(request, ClaimProfileRequest.objects.filter(id=reject_request.id))

    approve_request.refresh_from_db()
    reject_request.refresh_from_db()
    approve_request.company.refresh_from_db()
    assert approve_request.status == ClaimProfileRequest.Status.APPROVED
    assert approve_request.decided_at is not None
    assert approve_request.company.profile_status == Company.ProfileStatus.CLAIMED
    assert reject_request.status == ClaimProfileRequest.Status.REJECTED
    assert reject_request.decided_at is not None
    assert ClaimProfileModerationLog.objects.filter(claim=approve_request, action=ClaimProfileModerationLog.Action.APPROVED, moderator=user).exists()
    assert ClaimProfileModerationLog.objects.filter(claim=reject_request, action=ClaimProfileModerationLog.Action.REJECTED, moderator=user).exists()


@pytest.mark.django_db
def test_claim_profile_moderation_log_is_append_only_and_readable():
    user = get_user_model().objects.create_user(username="editor")
    claim = create_claim_request()
    log = ClaimProfileModerationLog.objects.create(
        claim=claim,
        moderator=user,
        action=ClaimProfileModerationLog.Action.REJECTED,
        from_status=ClaimProfileRequest.Status.PENDING,
        to_status=ClaimProfileRequest.Status.REJECTED,
        note="Need stronger proof",
    )

    assert str(log) == "Alma Remont alma-remont · Owner · rejected"
    assert log.created_at is not None


@pytest.mark.django_db
def test_claim_profile_moderation_logs_are_readonly_inline_on_claim_admin():
    request = RequestFactory().get("/admin/business/claimprofilerequest/1/change/")
    request.user = get_user_model().objects.create_superuser(username="moderator2", password="pass", email="m2@example.com")
    claim_admin = ClaimProfileRequestAdmin(ClaimProfileRequest, AdminSite())
    log_admin = ClaimProfileModerationLogAdmin(ClaimProfileModerationLog, AdminSite())
    inline = ClaimProfileModerationLogInline(ClaimProfileRequest, AdminSite())

    assert ClaimProfileModerationLogInline in claim_admin.inlines
    assert inline.extra == 0
    assert inline.can_delete is False
    assert inline.readonly_fields == ("moderator", "action", "from_status", "to_status", "note", "created_at")
    assert inline.has_add_permission(request, obj=create_claim_request()) is False
    assert log_admin.has_add_permission(request) is False
    assert log_admin.has_change_permission(request, obj=ClaimProfileModerationLog()) is False
