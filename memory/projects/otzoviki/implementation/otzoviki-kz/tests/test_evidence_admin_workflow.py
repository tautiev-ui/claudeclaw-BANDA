import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from django.utils import timezone

from apps.companies.models import Company
from apps.evidence.admin import EvidenceAdmin, EvidenceVisibilityLogAdmin, EvidenceVisibilityLogInline
from apps.evidence.models import Evidence, EvidenceVisibilityLog


def create_evidence(visibility=Evidence.Visibility.PRIVATE, evidence_type=Evidence.EvidenceType.EXTERNAL_FOOTPRINT):
    company = Company.objects.create(name="Alma Remont", slug=f"alma-remont-{visibility}-{evidence_type}")
    return Evidence.objects.create(
        company=company,
        evidence_type=evidence_type,
        title="Яндекс профиль найден",
        claim="Компания присутствует в Яндекс Картах",
        source_url="https://yandex.kz/maps/org/alma-remont/",
        visibility=visibility,
        captured_at=timezone.now(),
    )


@pytest.mark.django_db
def test_evidence_admin_visibility_actions_create_append_only_logs():
    user = get_user_model().objects.create_superuser(username="moderator", password="pass", email="m@example.com")
    request = RequestFactory().post("/admin/evidence/evidence/")
    request.user = user
    model_admin = EvidenceAdmin(Evidence, AdminSite())
    public_evidence = create_evidence(visibility=Evidence.Visibility.PRIVATE)
    private_evidence = create_evidence(visibility=Evidence.Visibility.PUBLIC)
    admin_only_evidence = create_evidence(visibility=Evidence.Visibility.PRIVATE, evidence_type=Evidence.EvidenceType.EDITORIAL_NOTE)

    model_admin.mark_public(request, Evidence.objects.filter(id=public_evidence.id))
    model_admin.mark_private(request, Evidence.objects.filter(id=private_evidence.id))
    model_admin.mark_admin_only(request, Evidence.objects.filter(id=admin_only_evidence.id))

    public_evidence.refresh_from_db()
    private_evidence.refresh_from_db()
    admin_only_evidence.refresh_from_db()
    assert public_evidence.visibility == Evidence.Visibility.PUBLIC
    assert private_evidence.visibility == Evidence.Visibility.PRIVATE
    assert admin_only_evidence.visibility == Evidence.Visibility.ADMIN_ONLY
    assert EvidenceVisibilityLog.objects.filter(evidence=public_evidence, action=EvidenceVisibilityLog.Action.MARK_PUBLIC, moderator=user).exists()
    assert EvidenceVisibilityLog.objects.filter(evidence=private_evidence, action=EvidenceVisibilityLog.Action.MARK_PRIVATE, moderator=user).exists()
    assert EvidenceVisibilityLog.objects.filter(evidence=admin_only_evidence, action=EvidenceVisibilityLog.Action.MARK_ADMIN_ONLY, moderator=user).exists()


@pytest.mark.django_db
def test_private_proof_cannot_be_marked_public_by_evidence_admin_action():
    user = get_user_model().objects.create_superuser(username="moderator2", password="pass", email="m2@example.com")
    request = RequestFactory().post("/admin/evidence/evidence/")
    request.user = user
    model_admin = EvidenceAdmin(Evidence, AdminSite())
    private_proof = create_evidence(visibility=Evidence.Visibility.PRIVATE, evidence_type=Evidence.EvidenceType.PRIVATE_PROOF)

    model_admin.mark_public(request, Evidence.objects.filter(id=private_proof.id))

    private_proof.refresh_from_db()
    assert private_proof.visibility == Evidence.Visibility.PRIVATE
    assert not private_proof.is_public
    assert EvidenceVisibilityLog.objects.filter(evidence=private_proof).count() == 0


@pytest.mark.django_db
def test_evidence_visibility_logs_are_readonly_inline_on_evidence_admin():
    request = RequestFactory().get("/admin/evidence/evidence/1/change/")
    request.user = get_user_model().objects.create_superuser(username="moderator3", password="pass", email="m3@example.com")
    evidence_admin = EvidenceAdmin(Evidence, AdminSite())
    log_admin = EvidenceVisibilityLogAdmin(EvidenceVisibilityLog, AdminSite())
    inline = EvidenceVisibilityLogInline(Evidence, AdminSite())

    assert EvidenceVisibilityLogInline in evidence_admin.inlines
    assert inline.extra == 0
    assert inline.can_delete is False
    assert inline.readonly_fields == ("moderator", "action", "from_visibility", "to_visibility", "note", "created_at")
    assert inline.has_add_permission(request, obj=create_evidence()) is False
    assert log_admin.has_add_permission(request) is False
    assert log_admin.has_change_permission(request, obj=EvidenceVisibilityLog()) is False
