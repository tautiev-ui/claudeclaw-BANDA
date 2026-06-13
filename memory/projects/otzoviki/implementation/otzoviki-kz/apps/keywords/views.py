import csv

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Q, Sum
from django.http import HttpResponse
from django.shortcuts import render

from apps.keywords.models import Keyword, KeywordCluster, KeywordPageMap, KeywordURLCompetitorEvidence


@staff_member_required(login_url="/admin/login/")
def keyword_report(request):
    top_queries = Keyword.objects.order_by("-frequency", "normalized_query")[:20]
    unmapped_queries = Keyword.objects.filter(clusters__isnull=True).order_by("-frequency", "normalized_query")[:20]
    cluster_stats = (
        KeywordCluster.objects.annotate(
            keyword_count=Count("keywords", distinct=True),
            page_map_count=Count("page_maps", distinct=True),
            frequency_sum=Sum("keywords__frequency"),
        )
        .order_by("slug")
    )
    top_evidence_domains = (
        KeywordURLCompetitorEvidence.objects.values("domain")
        .annotate(rows=Count("id"), top_10=Count("id", filter=Q(position__lte=10)))
        .order_by("-rows", "domain")[:20]
    )
    page_maps = KeywordPageMap.objects.select_related("cluster").order_by("priority", "page_type", "cluster__slug")[:50]
    totals = {
        "keyword_count": Keyword.objects.count(),
        "evidence_count": KeywordURLCompetitorEvidence.objects.count(),
        "cluster_count": KeywordCluster.objects.count(),
        "page_map_count": KeywordPageMap.objects.count(),
        "frequency_sum": Keyword.objects.aggregate(total=Sum("frequency"))["total"] or 0,
        "unmapped_count": Keyword.objects.filter(clusters__isnull=True).count(),
    }
    return render(
        request,
        "keywords/admin_report.html",
        {
            "page_title": "Keyword/page mapping report",
            "page_description": "Admin-only keyword and page mapping report.",
            "robots_meta": "noindex,follow",
            "canonical_url": request.build_absolute_uri("/admin/keywords/report/"),
            "totals": totals,
            "top_queries": top_queries,
            "unmapped_queries": unmapped_queries,
            "cluster_stats": cluster_stats,
            "top_evidence_domains": top_evidence_domains,
            "page_maps": page_maps,
        },
    )


@staff_member_required(login_url="/admin/login/")
def keyword_page_map_export_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="keyword-page-map-export.csv"'
    writer = csv.writer(response)
    writer.writerow([
        "cluster_slug",
        "page_type",
        "canonical_pattern",
        "priority",
        "is_indexable_candidate",
        "keyword_count",
        "frequency_sum",
        "evidence_count",
    ])
    page_maps = (
        KeywordPageMap.objects.select_related("cluster")
        .annotate(
            keyword_count=Count("cluster__keywords", distinct=True),
            frequency_sum=Sum("cluster__keywords__frequency"),
            evidence_count=Count("cluster__keywords__competitor_evidence", distinct=True),
        )
        .order_by("priority", "page_type", "cluster__slug", "canonical_pattern")
    )
    for page_map in page_maps:
        writer.writerow([
            page_map.cluster.slug,
            page_map.page_type,
            page_map.canonical_pattern,
            page_map.priority,
            page_map.is_indexable_candidate,
            page_map.keyword_count,
            page_map.frequency_sum or 0,
            page_map.evidence_count,
        ])
    return response


@staff_member_required(login_url="/admin/login/")
def markin_next_wave_export_csv(request):
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="markin-next-wave.csv"'
    fieldnames = ["cluster_slug", "cluster_name", "intent", "page_type", "priority", "canonical_pattern", "indexable_candidate", "next_action", "markin_stage"]
    writer = csv.DictWriter(response, fieldnames=fieldnames)
    writer.writeheader()
    page_maps = KeywordPageMap.objects.select_related("cluster").filter(cluster__slug__startswith="markin-next-").order_by("priority", "page_type", "cluster__slug")
    for page_map in page_maps:
        writer.writerow({
            "cluster_slug": page_map.cluster.slug,
            "cluster_name": page_map.cluster.name,
            "intent": page_map.cluster.intent,
            "page_type": page_map.page_type,
            "priority": page_map.priority,
            "canonical_pattern": page_map.canonical_pattern,
            "indexable_candidate": "true" if page_map.is_indexable_candidate else "false",
            "next_action": page_map.notes,
            "markin_stage": "Stage 6 page creation / Stage 7 relevance / Stage 8 boosters prep",
        })
    return response
