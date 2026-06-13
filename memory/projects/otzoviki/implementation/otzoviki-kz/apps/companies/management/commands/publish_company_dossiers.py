import csv
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.companies.models import Company
from apps.seo.indexability import IndexabilityStatus

REPORT_FIELDS = ["company_id", "name", "slug", "status", "reason", "verified_sources"]
METHODOLOGY_VERSION = "company-dossier-trust-gate-v1"


def evaluate_company(company):
    verified_sources = company.external_sources.filter(same_as_verified=True).count()
    missing = []
    if not company.is_active:
        missing.append("inactive")
    if not company.short_description.strip():
        missing.append("short_description")
    if not company.seo_title.strip():
        missing.append("seo_title")
    if not company.seo_description.strip():
        missing.append("seo_description")
    if not company.canonical_path.strip():
        missing.append("canonical_path")
    if not company.service_links.exists():
        missing.append("city_service_link")
    if verified_sources < 2:
        missing.append("verified_sources_lt_2")
    return verified_sources, missing


class Command(BaseCommand):
    help = "Promote imported company dossiers from noindex to indexable only when they pass the trust gate."

    def add_arguments(self, parser):
        parser.add_argument("--report", default="docs/company-publish-report.csv")
        parser.add_argument("--dry-run", action="store_true", help="Write report without mutating company indexability fields.")

    def handle(self, *args, **options):
        report_path = Path(options["report"])
        dry_run = options["dry_run"]
        report_path.parent.mkdir(parents=True, exist_ok=True)
        rows = []
        published = 0
        blocked = 0
        now = timezone.now()
        queryset = Company.objects.filter(index_status=IndexabilityStatus.NOINDEX.value).prefetch_related("external_sources", "service_links")
        for company in queryset.order_by("name", "id"):
            verified_sources, missing = evaluate_company(company)
            if missing:
                blocked += 1
                rows.append({
                    "company_id": company.pk,
                    "name": company.name,
                    "slug": company.slug,
                    "status": "blocked",
                    "reason": ";".join(missing),
                    "verified_sources": verified_sources,
                })
                continue
            status = "would_publish" if dry_run else "published"
            reason = "passes_company_dossier_trust_gate_v1"
            if not dry_run:
                company.index_status = IndexabilityStatus.INDEXABLE
                company.source_count = verified_sources
                company.last_verified_at = now
                company.methodology_version = METHODOLOGY_VERSION
                company.full_clean()
                company.save(update_fields=["index_status", "source_count", "last_verified_at", "methodology_version", "updated_at"])
                published += 1
            rows.append({
                "company_id": "" if dry_run else company.pk,
                "name": company.name,
                "slug": company.slug,
                "status": status,
                "reason": reason,
                "verified_sources": verified_sources,
            })
        with report_path.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=REPORT_FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        self.stdout.write(self.style.SUCCESS(f"Company publish gate processed={len(rows)} published={published} blocked={blocked} dry_run={dry_run} report={report_path}"))
