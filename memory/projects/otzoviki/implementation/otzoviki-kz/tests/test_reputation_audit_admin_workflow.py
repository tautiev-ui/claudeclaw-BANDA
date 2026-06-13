import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import RequestFactory

from apps.business.admin import ReputationAuditLeadAdmin, ReputationAuditLeadStatusLogAdmin, ReputationAuditLeadStatusLogInline
from apps.business.models import ReputationAuditLead, ReputationAuditLeadStatusLog
from apps.companies.models import Company


def create_audit_lead(status=ReputationAuditLead.Status.NEW, slug="alma-remont"):
    company = Company.objects.create(name=f"Alma Remont {slug}", slug=slug)
    return ReputationAuditLead.objects.create(
        company=company,
        contact_name="Айдар",
        contact_email="aidar@example.com",
        phone="+77000000000",
        source_page="/reputation-audit/",
        requested_surfaces=["yandex", "ai"],
        consent_given=True,
        status=status,
    )


@pytest.mark.django_db
def test_reputation_audit_lead_admin_status_actions_create_append_only_logs():
    user = get_user_model().objects.create_superuser(username="operator", password="pass", email="o@example.com")
    request = RequestFactory().post("/admin/business/reputationauditlead/")
    request.user = user
    model_admin = ReputationAuditLeadAdmin(ReputationAuditLead, AdminSite())
    contacted = create_audit_lead(slug="alma-remont-contacted")
    completed = create_audit_lead(slug="alma-remont-completed")

    model_admin.mark_contacted(request, ReputationAuditLead.objects.filter(id=contacted.id))
    model_admin.mark_completed(request, ReputationAuditLead.objects.filter(id=completed.id))

    contacted.refresh_from_db()
    completed.refresh_from_db()
    assert contacted.status == ReputationAuditLead.Status.CONTACTED
    assert completed.status == ReputationAuditLead.Status.COMPLETED
    assert ReputationAuditLeadStatusLog.objects.filter(lead=contacted, action=ReputationAuditLeadStatusLog.Action.CONTACTED, moderator=user).exists()
    assert ReputationAuditLeadStatusLog.objects.filter(lead=completed, action=ReputationAuditLeadStatusLog.Action.COMPLETED, moderator=user).exists()


@pytest.mark.django_db
def test_reputation_audit_status_logs_are_readonly_inline_on_lead_admin():
    request = RequestFactory().get("/admin/business/reputationauditlead/1/change/")
    request.user = get_user_model().objects.create_superuser(username="operator2", password="pass", email="o2@example.com")
    lead_admin = ReputationAuditLeadAdmin(ReputationAuditLead, AdminSite())
    log_admin = ReputationAuditLeadStatusLogAdmin(ReputationAuditLeadStatusLog, AdminSite())
    inline = ReputationAuditLeadStatusLogInline(ReputationAuditLead, AdminSite())

    assert ReputationAuditLeadStatusLogInline in lead_admin.inlines
    assert inline.extra == 0
    assert inline.can_delete is False
    assert inline.readonly_fields == ("moderator", "action", "from_status", "to_status", "note", "created_at")
    assert inline.has_add_permission(request, obj=create_audit_lead()) is False
    assert log_admin.has_add_permission(request) is False
    assert log_admin.has_change_permission(request, obj=ReputationAuditLeadStatusLog()) is False
