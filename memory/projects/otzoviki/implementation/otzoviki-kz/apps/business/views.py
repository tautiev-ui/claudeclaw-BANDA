from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.analytics.models import AnalyticsEvent, track_event
from apps.business.forms import ClaimProfileRequestForm, OfficialResponseSubmissionForm, ReputationAuditLeadForm
from apps.business.models import BusinessRepresentative
from apps.companies.models import Company


def breadcrumb_json_ld(request, name: str, canonical_path: str) -> str:
    return (
        '{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": ['
        '{"@type": "ListItem", "position": 1, "name": "Otzoviki KZ", "item": "'
        + request.build_absolute_uri("/")
        + '"}, '
        '{"@type": "ListItem", "position": 2, "name": "'
        + name
        + '", "item": "'
        + request.build_absolute_uri(canonical_path)
        + '"}'
        ']}'
    )


def claim_profile(request):
    if request.method == "POST":
        form = ClaimProfileRequestForm(request.POST)
        if form.is_valid():
            claim = form.save(request=request)
            track_event(event_type=AnalyticsEvent.EventType.CLAIM_PROFILE_SUBMIT, request=request, company=claim.company)
            return redirect("/claim-profile/?submitted=1")
    else:
        form = ClaimProfileRequestForm()
    return render(
        request,
        "business/claim_profile.html",
        {
            "form": form,
            "page_title": "Заявить профиль",
            "page_description": "Форма заявки на claim profile без влияния на рейтинг.",
            "robots_meta": "noindex,follow",
            "canonical_url": request.build_absolute_uri("/claim-profile/"),
            "breadcrumb_json_ld": breadcrumb_json_ld(request, "Заявить профиль", "/claim-profile/"),
        },
    )


def reputation_audit(request):
    if request.method == "POST":
        form = ReputationAuditLeadForm(request.POST)
        if form.is_valid():
            lead = form.save(request=request)
            track_event(event_type=AnalyticsEvent.EventType.AUDIT_LEAD_SUBMIT, request=request, company=lead.company, metadata={"requested_surfaces": lead.requested_surfaces})
            return redirect("/reputation-audit/?submitted=1")
    else:
        form = ReputationAuditLeadForm()
    return render(
        request,
        "business/reputation_audit.html",
        {
            "form": form,
            "page_title": "Аудит репутации",
            "page_description": "Заявка на аудит Otzoviki/Yandex/2GIS/Google/AI surfaces.",
            "robots_meta": "noindex,follow",
            "canonical_url": request.build_absolute_uri("/reputation-audit/"),
            "breadcrumb_json_ld": breadcrumb_json_ld(request, "Аудит репутации", "/reputation-audit/"),
        },
    )


@login_required(login_url="/admin/login/")
def private_business_workspace(request, path: str = "dashboard"):
    canonical_path = request.path
    all_representatives = BusinessRepresentative.objects.filter(
        email__iexact=request.user.email,
    ).select_related("account__company").order_by("account__company__name", "full_name")
    verified_representatives = [representative for representative in all_representatives if representative.is_verified]
    pending_representatives = [representative for representative in all_representatives if not representative.is_verified]
    managed_companies = [representative.account.company for representative in verified_representatives if representative.can_manage_profile]
    return render(
        request,
        "business/private_workspace.html",
        {
            "user_email": request.user.email,
            "verified_representatives": verified_representatives,
            "pending_representatives": pending_representatives,
            "managed_companies": managed_companies,
            "page_title": "Business dashboard",
            "page_description": "Private business workspace for Otzoviki KZ.",
            "robots_meta": "noindex,follow",
            "canonical_url": request.build_absolute_uri(canonical_path),
            "breadcrumb_json_ld": breadcrumb_json_ld(request, "Business dashboard", canonical_path),
        },
    )


def verified_representative_for_request(request, company):
    user_email = getattr(getattr(request, "user", None), "email", "")
    if not user_email:
        return None
    return BusinessRepresentative.objects.filter(
        account__company=company,
        email__iexact=user_email,
        verification_status=BusinessRepresentative.VerificationStatus.APPROVED,
        email_verified=True,
    ).select_related("account").first()


def submit_official_response(request, slug: str):
    company = get_object_or_404(Company, slug=slug)
    verified_representative = verified_representative_for_request(request, company)
    if request.method == "POST":
        form = OfficialResponseSubmissionForm(request.POST)
        if form.is_valid():
            form.save(company=company, request=request)
            return redirect(company.get_absolute_url())
    else:
        initial = {}
        if verified_representative:
            initial = {
                "contact_name": verified_representative.full_name,
                "contact_email": verified_representative.email,
                "role_title": verified_representative.role_title,
            }
        form = OfficialResponseSubmissionForm(initial=initial)
    canonical_path = f"{company.get_absolute_url()}official-response/new/"
    return render(
        request,
        "business/submit_official_response.html",
        {
            "company": company,
            "form": form,
            "verified_representative": verified_representative,
            "page_title": f"Официальный ответ — {company.name}",
            "page_description": "Форма официального ответа компании с модерацией.",
            "robots_meta": "noindex,follow",
            "canonical_url": request.build_absolute_uri(canonical_path),
            "breadcrumb_json_ld": breadcrumb_json_ld(request, "Официальный ответ", canonical_path),
        },
    )
