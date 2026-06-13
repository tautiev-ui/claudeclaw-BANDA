import csv
import re
from pathlib import Path
from urllib.parse import urlparse

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.companies.models import Company, CompanyService
from apps.evidence.models import ExternalSource
from apps.locations.models import City, Country
from apps.seo.indexability import IndexabilityStatus
from apps.services.models import Service, ServiceCategory

REPORT_FIELDS = ["row_number", "name", "slug", "status", "reason", "company_id"]
REQUIRED_FIELDS = ["name", "city_slug", "service_slug", "website_url", "phone", "yandex_url", "two_gis_url", "short_description"]
TRANSLIT = {ord(src): dst for src, dst in {
    "а":"a","б":"b","в":"v","г":"g","д":"d","е":"e","ё":"e","ж":"zh","з":"z","и":"i","й":"y","к":"k","л":"l","м":"m","н":"n","о":"o","п":"p","р":"r","с":"s","т":"t","у":"u","ф":"f","х":"h","ц":"c","ч":"ch","ш":"sh","щ":"sch","ъ":"","ы":"y","ь":"","э":"e","ю":"u","я":"ya",
}.items()}


def normalize_url(url):
    value = (url or "").strip()
    if not value:
        return ""
    parsed = urlparse(value)
    scheme = parsed.scheme.lower() or "https"
    netloc = parsed.netloc.lower()
    path = parsed.path.rstrip("/")
    if not netloc and parsed.path:
        parsed = urlparse("https://" + value)
        scheme = parsed.scheme.lower()
        netloc = parsed.netloc.lower()
        path = parsed.path.rstrip("/")
    return f"{scheme}://{netloc}{path}"


def slugify_ascii(name):
    value = name.lower().translate(TRANSLIT)
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or "company"


def unique_slug(base):
    slug = base
    suffix = 2
    while Company.objects.filter(slug=slug).exists():
        slug = f"{base}-{suffix}"
        suffix += 1
    return slug


class Command(BaseCommand):
    help = "Import real company dossier CSV as draft/noindex records with validation report."

    def add_arguments(self, parser):
        parser.add_argument("csv_path")
        parser.add_argument("--report", default="docs/company-import-report.csv")

    def handle(self, *args, **options):
        csv_path = Path(options["csv_path"])
        if not csv_path.exists():
            raise CommandError(f"CSV not found: {csv_path}")
        report_path = Path(options["report"])
        report_path.parent.mkdir(parents=True, exist_ok=True)
        now = timezone.now()
        kz, _ = Country.objects.get_or_create(code="KZ", defaults={"name": "Казахстан", "slug": "kz", "is_active": True})
        service_category, _ = ServiceCategory.objects.get_or_create(slug="remont-i-stroitelstvo", defaults={"name": "Ремонт и строительство", "is_active": True})
        rows_out = []
        seen_websites = set(Company.objects.exclude(website_url="").values_list("website_url", flat=True))
        seen_yandex = set(ExternalSource.objects.filter(source_type=ExternalSource.SourceType.YANDEX).values_list("url", flat=True))
        seen_2gis = set(ExternalSource.objects.filter(source_type=ExternalSource.SourceType.TWO_GIS).values_list("url", flat=True))
        with csv_path.open(newline="") as handle:
            reader = csv.DictReader(handle)
            missing = [field for field in REQUIRED_FIELDS if field not in (reader.fieldnames or [])]
            if missing:
                raise CommandError(f"Missing required fields: {', '.join(missing)}")
            for row_number, row in enumerate(reader, start=2):
                name = (row.get("name") or "").strip()
                website = normalize_url(row.get("website_url"))
                yandex_url = normalize_url(row.get("yandex_url"))
                two_gis_url = normalize_url(row.get("two_gis_url"))
                if not name:
                    rows_out.append({"row_number": row_number, "name": name, "slug": "", "status": "error", "reason": "missing_name", "company_id": ""})
                    continue
                if website and website in seen_websites:
                    rows_out.append({"row_number": row_number, "name": name, "slug": "", "status": "duplicate", "reason": "duplicate_website_url", "company_id": ""})
                    continue
                if yandex_url and yandex_url in seen_yandex:
                    rows_out.append({"row_number": row_number, "name": name, "slug": "", "status": "duplicate", "reason": "duplicate_yandex_url", "company_id": ""})
                    continue
                if two_gis_url and two_gis_url in seen_2gis:
                    rows_out.append({"row_number": row_number, "name": name, "slug": "", "status": "duplicate", "reason": "duplicate_2gis_url", "company_id": ""})
                    continue
                city_slug = (row.get("city_slug") or "").strip() or "unknown"
                service_slug = (row.get("service_slug") or "").strip() or "remont-kvartir"
                city, _ = City.objects.get_or_create(country=kz, slug=city_slug, defaults={"name": city_slug.replace("-", " ").title(), "is_active": True})
                service, _ = Service.objects.get_or_create(slug=service_slug, defaults={"category": service_category, "name": service_slug.replace("-", " ").title(), "is_active": True})
                base_slug = slugify_ascii(name)
                slug = unique_slug(base_slug)
                company = Company.objects.create(
                    name=name,
                    slug=slug,
                    short_description=(row.get("short_description") or "").strip(),
                    website_url=website,
                    phone=(row.get("phone") or "").strip(),
                    is_active=True,
                    index_status=IndexabilityStatus.NOINDEX.value,
                    seo_title=f"{name} — досье Otzoviki KZ",
                    seo_description=(row.get("short_description") or "").strip(),
                    canonical_path=f"/kz/company/{slug}/",
                    source_count=0,
                    last_verified_at=None,
                    methodology_version="",
                )
                CompanyService.objects.get_or_create(company=company, city=city, service=service, defaults={"is_primary": True})
                if yandex_url:
                    ExternalSource.objects.create(company=company, source_type=ExternalSource.SourceType.YANDEX, name="Яндекс Бизнес", url=yandex_url, same_as_verified=False, captured_at=now)
                    seen_yandex.add(yandex_url)
                if two_gis_url:
                    ExternalSource.objects.create(company=company, source_type=ExternalSource.SourceType.TWO_GIS, name="2ГИС", url=two_gis_url, same_as_verified=False, captured_at=now)
                    seen_2gis.add(two_gis_url)
                if website:
                    seen_websites.add(website)
                rows_out.append({"row_number": row_number, "name": name, "slug": slug, "status": "created", "reason": "draft_noindex", "company_id": company.pk})
        with report_path.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=REPORT_FIELDS)
            writer.writeheader()
            writer.writerows(rows_out)
        self.stdout.write(self.style.SUCCESS(f"Company import processed {len(rows_out)} rows; report={report_path}"))
