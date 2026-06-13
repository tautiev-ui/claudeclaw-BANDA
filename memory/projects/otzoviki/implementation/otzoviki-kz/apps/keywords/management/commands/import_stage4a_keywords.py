import csv

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.keywords.models import Keyword, KeywordCluster, KeywordPageMap, KeywordURLCompetitorEvidence


PAGE_TYPE_MAP = {
    "company_reputation_dossier": KeywordPageMap.PageType.COMPANY_DOSSIER.value,
    "company_reputation_dossier_or_reviews_cluster": KeywordPageMap.PageType.COMPANY_DOSSIER.value,
    "geo_service_page": KeywordPageMap.PageType.CITY_SERVICE.value,
    "service_cluster_or_guide": KeywordPageMap.PageType.CITY_SERVICE.value,
    "ranking_or_best_page": KeywordPageMap.PageType.RANKING.value,
    "price_guide_or_calculator": KeywordPageMap.PageType.PRICE.value,
    "guide": KeywordPageMap.PageType.GUIDE.value,
}

CANONICAL_PATTERNS = {
    KeywordPageMap.PageType.COMPANY_DOSSIER.value: "/kz/company/{company_slug}/",
    KeywordPageMap.PageType.CITY_SERVICE.value: "/kz/{city}/{service_slug}/",
    KeywordPageMap.PageType.RANKING.value: "/kz/{city}/reyting-remontnyh-kompaniy/",
    KeywordPageMap.PageType.PRICE.value: "/kz/{city}/remont-kvartir/ceny/",
    KeywordPageMap.PageType.CITY_HUB.value: "/kz/{city}/",
    KeywordPageMap.PageType.GUIDE.value: "/kz/guides/{slug}/",
    KeywordPageMap.PageType.OTHER.value: "/",
}

CLUSTER_CANONICAL_PATTERNS = {
    "apartment_repair": "/kz/{city}/remont-kvartir/",
    "contractor_reputation": "/kz/{city}/reyting-remontnyh-kompaniy/",
    "engineering_services": "/kz/{city}/{service_slug}/",
    "house_construction": "/kz/{city}/stroitelstvo-domov/",
    "interior_design": "/kz/{city}/dizayn-interera/",
    "newbuild_developer": "/kz/{city}/novostroyki/",
    "windows_doors_finish": "/kz/{city}/{service_slug}/",
}

MONEY_PAGE_TYPES = {
    KeywordPageMap.PageType.COMPANY_DOSSIER.value,
    KeywordPageMap.PageType.CITY_SERVICE.value,
    KeywordPageMap.PageType.RANKING.value,
    KeywordPageMap.PageType.PRICE.value,
    KeywordPageMap.PageType.CITY_HUB.value,
}


class Command(BaseCommand):
    help = "Import Stage 4A Keys.so keyword and keyword→URL evidence CSV files."

    def add_arguments(self, parser):
        parser.add_argument("--queries", required=True, help="Path to strict_target_queries.csv")
        parser.add_argument("--evidence", required=False, help="Path to keyword_url_onpage_join.csv")

    @transaction.atomic
    def handle(self, *args, **options):
        query_count = import_queries(options["queries"])
        evidence_count = import_evidence(options.get("evidence")) if options.get("evidence") else 0
        cluster_count, page_map_count = build_clusters_and_page_maps()
        self.stdout.write(
            self.style.SUCCESS(
                f"Imported {query_count} keywords, {evidence_count} evidence rows, "
                f"{cluster_count} clusters and {page_map_count} page maps"
            )
        )


def import_queries(path: str) -> int:
    imported = 0
    seen = set()
    with open(path, encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            query = (row.get("query_norm") or row.get("query") or "").strip()
            normalized = normalize_query(query)
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            keyword, created = Keyword.objects.update_or_create(
                normalized_query=normalized,
                defaults={
                    "query": query,
                    "frequency": safe_int(row.get("freq_base_sum") or row.get("freq_base")),
                    "source": Keyword.Source.KEYS_SO,
                    "region": row.get("region") or "kz",
                    "target_cluster": row.get("target_cluster") or row.get("suggested_page_type") or "",
                },
            )
            imported += 1 if created else 0
            if not created:
                keyword.save()
    return imported


def import_evidence(path: str) -> int:
    imported = 0
    with open(path, encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            query = (row.get("query_norm") or row.get("query") or "").strip()
            normalized = normalize_query(query)
            if not normalized:
                continue
            keyword, _ = Keyword.objects.get_or_create(
                normalized_query=normalized,
                defaults={
                    "query": query,
                    "frequency": safe_int(row.get("freq_base")),
                    "source": Keyword.Source.KEYS_SO,
                    "region": row.get("region") or "kz",
                    "target_cluster": row.get("target_cluster") or row.get("suggested_page_type") or "",
                },
            )
            _, created = KeywordURLCompetitorEvidence.objects.get_or_create(
                keyword=keyword,
                url=(row.get("url") or "").strip(),
                defaults={
                    "domain": row.get("domain") or "",
                    "title": row.get("onpage_title") or row.get("title") or "",
                    "h1": row.get("onpage_h1") or row.get("h1") or "",
                    "position": safe_int_or_none(row.get("position")),
                },
            )
            imported += 1 if created else 0
    return imported


def build_clusters_and_page_maps() -> tuple[int, int]:
    cluster_count = 0
    page_map_count = 0
    cluster_slugs = (
        Keyword.objects.exclude(target_cluster="")
        .values_list("target_cluster", flat=True)
        .distinct()
        .order_by("target_cluster")
    )
    for slug in cluster_slugs:
        keywords = Keyword.objects.filter(target_cluster=slug)
        page_type = infer_page_type(slug)
        cluster, created = KeywordCluster.objects.get_or_create(
            slug=slug,
            defaults={
                "name": slug.replace("_", " ").replace("-", " "),
                "intent": infer_intent(slug, page_type),
                "page_type": page_type,
            },
        )
        if not created and not cluster.page_type:
            cluster.page_type = page_type
            cluster.intent = infer_intent(slug, page_type)
            cluster.save(update_fields=["page_type", "intent", "updated_at"])
        cluster.keywords.add(*keywords)
        cluster_count += 1 if created else 0
        canonical_pattern = infer_canonical_pattern(slug, page_type)
        page_map, page_map_created = KeywordPageMap.objects.get_or_create(
            cluster=cluster,
            page_type=page_type,
            canonical_pattern=canonical_pattern,
            defaults={
                "priority": KeywordPageMap.Priority.P0 if page_type in MONEY_PAGE_TYPES else KeywordPageMap.Priority.P1,
                "is_indexable_candidate": False,
                "notes": "Generated from Stage 4A target_cluster during Markin keyword ingestion. Keep noindex until data/trust gates pass.",
            },
        )
        retire_stale_generated_page_maps(cluster, page_type, canonical_pattern)
        page_map_count += 1 if page_map_created else 0
    return cluster_count, page_map_count


def infer_canonical_pattern(cluster_slug: str, page_type: str) -> str:
    return CLUSTER_CANONICAL_PATTERNS.get(
        cluster_slug,
        CANONICAL_PATTERNS.get(page_type, CANONICAL_PATTERNS[KeywordPageMap.PageType.OTHER.value]),
    )


def retire_stale_generated_page_maps(cluster: KeywordCluster, page_type: str, canonical_pattern: str) -> None:
    KeywordPageMap.objects.filter(
        cluster=cluster,
        page_type=page_type,
        notes__startswith="Generated from Stage 4A",
    ).exclude(canonical_pattern=canonical_pattern).delete()


def infer_page_type(marker: str) -> str:
    marker = (marker or "").lower()
    for key, page_type in PAGE_TYPE_MAP.items():
        if key in marker:
            return page_type
    if "price" in marker or "smeta" in marker or "calculator" in marker:
        return KeywordPageMap.PageType.PRICE.value
    if "ranking" in marker or "best" in marker or "reputation" in marker:
        return KeywordPageMap.PageType.RANKING.value
    if "guide" in marker or "inform" in marker:
        return KeywordPageMap.PageType.GUIDE.value
    if "company" in marker or "contractor" in marker:
        return KeywordPageMap.PageType.COMPANY_DOSSIER.value
    return KeywordPageMap.PageType.CITY_SERVICE.value


def infer_intent(marker: str, page_type: str) -> str:
    marker = marker.lower()
    if page_type in MONEY_PAGE_TYPES:
        return KeywordCluster.Intent.COMMERCIAL.value
    if page_type == KeywordPageMap.PageType.GUIDE.value or "guide" in marker:
        return KeywordCluster.Intent.INFORMATIONAL.value
    return KeywordCluster.Intent.MIXED.value


def normalize_query(query: str) -> str:
    return " ".join(query.strip().lower().split())


def safe_int(value) -> int:
    return safe_int_or_none(value) or 0


def safe_int_or_none(value):
    try:
        if value in (None, ""):
            return None
        return int(float(value))
    except (TypeError, ValueError):
        return None


