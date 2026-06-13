import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.test import RequestFactory

from apps.ai_evidence.admin import AIYandexEvidenceLogAdmin, AIYandexEvidenceVisibilityLogAdmin, AIYandexEvidenceVisibilityLogInline
from apps.ai_evidence.models import AIYandexEvidenceLog, AIYandexEvidenceVisibilityLog
from apps.companies.models import Company


def create_ai_log(visibility=AIYandexEvidenceLog.Visibility.PRIVATE, *, screenshot=False):
    slug = f"alma-remont-ai-{visibility}-{int(screenshot)}-{Company.objects.count()}"
    company = Company.objects.create(name="Alma Remont", slug=slug)
    log = AIYandexEvidenceLog.objects.create(
        company=company,
        platform=AIYandexEvidenceLog.Platform.YANDEX_NEURO,
        query="Alma Remont отзывы",
        region="Алматы",
        answer_excerpt="Компания упоминается в нейроответе.",
        cited_sources=["https://yandex.kz/maps/org/example/"],
        sentiment=AIYandexEvidenceLog.Sentiment.MIXED,
        visibility=visibility,
    )
    if screenshot:
        log.screenshot.save("sensitive.png", ContentFile(b"fake-image"), save=True)
    return log


@pytest.mark.django_db
def test_ai_evidence_admin_visibility_actions_create_append_only_logs():
    user = get_user_model().objects.create_superuser(username="moderator", password="pass", email="m@example.com")
    request = RequestFactory().post("/admin/ai_evidence/aiyandexevidencelog/")
    request.user = user
    model_admin = AIYandexEvidenceLogAdmin(AIYandexEvidenceLog, AdminSite())
    public_log = create_ai_log(visibility=AIYandexEvidenceLog.Visibility.PRIVATE)
    private_log = create_ai_log(visibility=AIYandexEvidenceLog.Visibility.PUBLIC)
    admin_only_log = create_ai_log(visibility=AIYandexEvidenceLog.Visibility.PRIVATE)

    model_admin.mark_public(request, AIYandexEvidenceLog.objects.filter(id=public_log.id))
    model_admin.mark_private(request, AIYandexEvidenceLog.objects.filter(id=private_log.id))
    model_admin.mark_admin_only(request, AIYandexEvidenceLog.objects.filter(id=admin_only_log.id))

    public_log.refresh_from_db()
    private_log.refresh_from_db()
    admin_only_log.refresh_from_db()
    assert public_log.visibility == AIYandexEvidenceLog.Visibility.PUBLIC
    assert private_log.visibility == AIYandexEvidenceLog.Visibility.PRIVATE
    assert admin_only_log.visibility == AIYandexEvidenceLog.Visibility.ADMIN_ONLY
    assert AIYandexEvidenceVisibilityLog.objects.filter(log=public_log, action=AIYandexEvidenceVisibilityLog.Action.MARK_PUBLIC, moderator=user).exists()
    assert AIYandexEvidenceVisibilityLog.objects.filter(log=private_log, action=AIYandexEvidenceVisibilityLog.Action.MARK_PRIVATE, moderator=user).exists()
    assert AIYandexEvidenceVisibilityLog.objects.filter(log=admin_only_log, action=AIYandexEvidenceVisibilityLog.Action.MARK_ADMIN_ONLY, moderator=user).exists()


@pytest.mark.django_db
def test_ai_evidence_with_screenshot_cannot_be_marked_public_by_admin_action(settings):
    settings.MEDIA_ROOT = "/tmp/otzoviki-test-media"
    user = get_user_model().objects.create_superuser(username="moderator2", password="pass", email="m2@example.com")
    request = RequestFactory().post("/admin/ai_evidence/aiyandexevidencelog/")
    request.user = user
    model_admin = AIYandexEvidenceLogAdmin(AIYandexEvidenceLog, AdminSite())
    screenshot_log = create_ai_log(visibility=AIYandexEvidenceLog.Visibility.PRIVATE, screenshot=True)

    model_admin.mark_public(request, AIYandexEvidenceLog.objects.filter(id=screenshot_log.id))

    screenshot_log.refresh_from_db()
    assert screenshot_log.visibility == AIYandexEvidenceLog.Visibility.PRIVATE
    assert not screenshot_log.is_public_safe
    assert AIYandexEvidenceVisibilityLog.objects.filter(log=screenshot_log).count() == 0


@pytest.mark.django_db
def test_ai_evidence_visibility_logs_are_readonly_inline_on_admin():
    request = RequestFactory().get("/admin/ai_evidence/aiyandexevidencelog/1/change/")
    request.user = get_user_model().objects.create_superuser(username="moderator3", password="pass", email="m3@example.com")
    evidence_admin = AIYandexEvidenceLogAdmin(AIYandexEvidenceLog, AdminSite())
    log_admin = AIYandexEvidenceVisibilityLogAdmin(AIYandexEvidenceVisibilityLog, AdminSite())
    inline = AIYandexEvidenceVisibilityLogInline(AIYandexEvidenceLog, AdminSite())

    assert AIYandexEvidenceVisibilityLogInline in evidence_admin.inlines
    assert inline.extra == 0
    assert inline.can_delete is False
    assert inline.readonly_fields == ("moderator", "action", "from_visibility", "to_visibility", "note", "created_at")
    assert inline.has_add_permission(request, obj=create_ai_log()) is False
    assert log_admin.has_add_permission(request) is False
    assert log_admin.has_change_permission(request, obj=AIYandexEvidenceVisibilityLog()) is False
