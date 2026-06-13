import csv

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse

from apps.companies.models import Company
from apps.companies.management.commands.publish_company_dossiers import evaluate_company
from apps.seo.indexability import IndexabilityStatus

PUBLISH_READINESS_FIELDS = [
    "company_id",
    "name",
    "slug",
    "status",
    "reason",
    "verified_sources",
    "would_index",
    "current_index_status",
]


@staff_member_required(login_url="/admin/login/")
def company_publish_readiness_csv(request):
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="company-publish-readiness.csv"'
    writer = csv.DictWriter(response, fieldnames=PUBLISH_READINESS_FIELDS)
    writer.writeheader()
    queryset = Company.objects.filter(index_status=IndexabilityStatus.NOINDEX.value).prefetch_related("external_sources", "service_links").order_by("name", "id")
    for company in queryset:
        verified_sources, missing = evaluate_company(company)
        writer.writerow({
            "company_id": company.pk,
            "name": company.name,
            "slug": company.slug,
            "status": "blocked" if missing else "ready",
            "reason": ";".join(missing) if missing else "passes_company_dossier_trust_gate_v1",
            "verified_sources": verified_sources,
            "would_index": "false" if missing else "true",
            "current_index_status": company.index_status,
        })
    return response
