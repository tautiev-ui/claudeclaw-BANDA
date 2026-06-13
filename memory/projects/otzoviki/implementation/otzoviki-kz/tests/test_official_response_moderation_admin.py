import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import RequestFactory

from apps.business.admin import OfficialResponseAdmin
from apps.business.models import OfficialResponse, OfficialResponseModerationLog
from apps.companies.models import Company


def create_official_response(status=OfficialResponse.Status.PENDING, slug="alma-remont"):
    company = Company.objects.create(name=f"Alma Remont {slug}", slug=slug)
    return OfficialResponse.objects.create(
        company=company,
        body="Официальная позиция компании по обращению клиента.",
        status=status,
        source_page=company.get_absolute_url(),
    )


@pytest.mark.django_db
def test_official_response_admin_actions_publish_reject_and_log():
    user = get_user_model().objects.create_superuser(username="moderator", password="pass", email="m@example.com")
    request = RequestFactory().post("/admin/business/officialresponse/")
    request.user = user
    model_admin = OfficialResponseAdmin(OfficialResponse, AdminSite())

    publish_response = create_official_response(slug="publish-official")
    reject_response = create_official_response(slug="reject-official")

    model_admin.mark_published(request, OfficialResponse.objects.filter(id=publish_response.id))
    model_admin.mark_rejected(request, OfficialResponse.objects.filter(id=reject_response.id))

    publish_response.refresh_from_db()
    reject_response.refresh_from_db()
    assert publish_response.status == OfficialResponse.Status.PUBLISHED
    assert publish_response.published_at is not None
    assert reject_response.status == OfficialResponse.Status.REJECTED
    assert reject_response.published_at is None
    assert OfficialResponseModerationLog.objects.filter(response=publish_response, action=OfficialResponseModerationLog.Action.PUBLISHED, moderator=user).exists()
    assert OfficialResponseModerationLog.objects.filter(response=reject_response, action=OfficialResponseModerationLog.Action.REJECTED, moderator=user).exists()


@pytest.mark.django_db
def test_official_response_moderation_log_is_append_only_and_readable():
    user = get_user_model().objects.create_user(username="editor")
    response = create_official_response()
    log = OfficialResponseModerationLog.objects.create(
        response=response,
        moderator=user,
        action=OfficialResponseModerationLog.Action.REJECTED,
        from_status=OfficialResponse.Status.PENDING,
        to_status=OfficialResponse.Status.REJECTED,
        note="Needs proof",
    )

    assert str(log) == "Alma Remont alma-remont · official response · rejected"
    assert log.created_at is not None
