import csv
from pathlib import Path
from urllib.parse import urlparse

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.companies.management.commands.import_company_dossiers import normalize_url, slugify_ascii
from apps.companies.models import Company
from apps.evidence.models import ExternalSource

REQUIRED_FIELDS = ["name", "website_url", "yandex_url", "two_gis_url"]
REPORT_FIELDS = ["row_number", "name", "company_id", "slug", "status", "reason", "sources_verified"]
SOURCE_SPECS = [
    ("yandex_url", ExternalSource.SourceType.YANDEX, "Яндекс Бизнес"),
    ("two_gis_url", ExternalSource.SourceType.TWO_GIS, "2ГИС"),
]


def normalized_url_variants(url: str) -> set[str]:
    normalized = normalize_url(url)
    if not normalized:
        return set()
    variants = {normalized, normalized.rstrip("/")}
    parsed = urlparse(normalized)
    if parsed.netloc == "yandex.ru":
        variants.add(normalized.replace("https://yandex.ru/", "https://yandex.kz/", 1))
    if parsed.netloc == "yandex.kz":
        variants.add(normalized.replace("https://yandex.kz/", "https://yandex.ru/", 1))
    return {variant.rstrip("/") for variant in variants if variant}


def find_company(row):
    source_urls = []
    for field, source_type, _name in SOURCE_SPECS:
        for variant in normalized_url_variants(row.get(field)):
            source_urls.append((source_type, variant))
    for source_type, url in source_urls:
        source = ExternalSource.objects.filter(source_type=source_type, url__in=[url, f"{url}/"]).select_related("company").first()
        if source:
            return source.company

    website = normalize_url(row.get("website_url"))
    if website:
        company = Company.objects.filter(website_url__in=[website, f"{website}/"]).first()
        if company:
            return company

    name = (row.get("name") or "").strip()
    if name:
        company = Company.objects.filter(name__iexact=name).first()
        if company:
            return company
        slug = slugify_ascii(name)
        company = Company.objects.filter(slug=slug).first()
        if company:
            return company
    return None


class Command(BaseCommand):
    help = "Attach verified Yandex/2GIS ExternalSource rows from a verified evidence CSV."

    def add_arguments(self, parser):
        parser.add_argument("csv_path")
        parser.add_argument("--report", default="docs/company-verified-external-sources-report.csv")
        parser.add_argument("--dry-run", action="store_true", help="Validate and report without writing ExternalSource changes.")

    def handle(self, *args, **options):
        csv_path = Path(options["csv_path"])
        if not csv_path.exists():
            raise CommandError(f"CSV not found: {csv_path}")
        report_path = Path(options["report"])
        report_path.parent.mkdir(parents=True, exist_ok=True)
        dry_run = options["dry_run"]
        now = timezone.now()
        rows_out = []
        processed = updated = blocked = 0
        with csv_path.open(newline="") as handle:
            reader = csv.DictReader(handle)
            missing = [field for field in REQUIRED_FIELDS if field not in (reader.fieldnames or [])]
            if missing:
                raise CommandError(f"Missing required fields: {', '.join(missing)}")
            for row_number, row in enumerate(reader, start=2):
                processed += 1
                name = (row.get("name") or "").strip()
                company = find_company(row)
                urls = []
                for field, source_type, source_name in SOURCE_SPECS:
                    url = normalize_url(row.get(field))
                    if url:
                        urls.append((source_type, source_name, url))
                if not company:
                    blocked += 1
                    rows_out.append({
                        "row_number": row_number,
                        "name": name,
                        "company_id": "",
                        "slug": "",
                        "status": "blocked",
                        "reason": "company_not_found",
                        "sources_verified": len(urls),
                    })
                    continue
                if len(urls) < 2:
                    blocked += 1
                    rows_out.append({
                        "row_number": row_number,
                        "name": name,
                        "company_id": company.pk,
                        "slug": company.slug,
                        "status": "blocked",
                        "reason": "verified_sources_lt_2_in_csv",
                        "sources_verified": len(urls),
                    })
                    continue
                if dry_run:
                    rows_out.append({
                        "row_number": row_number,
                        "name": name,
                        "company_id": company.pk,
                        "slug": company.slug,
                        "status": "dry_run",
                        "reason": "would_attach_verified_sources",
                        "sources_verified": len(urls),
                    })
                    continue
                for source_type, source_name, url in urls:
                    source, _created = ExternalSource.objects.get_or_create(
                        company=company,
                        source_type=source_type,
                        url=url,
                        defaults={"name": source_name, "same_as_verified": True, "captured_at": now},
                    )
                    if not source.same_as_verified or source.name != source_name:
                        source.same_as_verified = True
                        source.name = source_name
                        source.captured_at = now
                        source.save(update_fields=["same_as_verified", "name", "captured_at"])
                updated += 1
                rows_out.append({
                    "row_number": row_number,
                    "name": name,
                    "company_id": company.pk,
                    "slug": company.slug,
                    "status": "updated",
                    "reason": "verified_sources_attached",
                    "sources_verified": len(urls),
                })
        with report_path.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=REPORT_FIELDS)
            writer.writeheader()
            writer.writerows(rows_out)
        self.stdout.write(self.style.SUCCESS(f"Verified source import processed={processed} updated={updated} blocked={blocked} dry_run={dry_run} report={report_path}"))
