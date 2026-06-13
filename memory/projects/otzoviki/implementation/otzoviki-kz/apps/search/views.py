from django.http import JsonResponse
from django.shortcuts import render

from apps.analytics.models import AnalyticsEvent, track_event
from apps.companies.models import Company
from apps.guides.models import Guide
from apps.keywords.models import Keyword
from apps.locations.models import City
from apps.search.models import SearchQuery, normalize_query
from apps.services.models import Service


def search_view(request):
    query = request.GET.get("q", "")
    normalized = normalize_query(query)
    results = build_results(normalized) if normalized else []
    SearchQuery.record(query, len(results)) if normalized else None
    if normalized:
        track_event(event_type=AnalyticsEvent.EventType.SEARCH, request=request, query=normalized, metadata={"result_count": len(results)})
    return render(
        request,
        "search/results.html",
        {
            "page_title": f"Поиск: {query}" if query else "Поиск",
            "page_description": "Поиск по компаниям, городам, услугам и гайдам Otzoviki KZ.",
            "robots_meta": "noindex,follow",
            "canonical_url": request.build_absolute_uri(request.path),
            "query": query,
            "results": results,
            "breadcrumb_json_ld": '{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": []}',
        },
    )


def autocomplete_view(request):
    query = request.GET.get("q", "")
    normalized = normalize_query(query)
    if len(normalized) < 2:
        return JsonResponse({"query": normalized, "results": []})
    results = build_results(normalized, include_keywords=True)[:10]
    return JsonResponse({"query": normalized, "results": results})


def build_results(normalized: str, *, include_keywords: bool = False) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    for company in Company.objects.filter(name__icontains=normalized.split()[0])[:8]:
        if normalized in company.name.lower() or company.name.lower() in normalized or normalized.split()[0] in company.name.lower():
            results.append({"type": "company", "title": company.name, "url": company.get_absolute_url()})

    cities = list(City.objects.active())
    services = list(Service.objects.active())
    for city in cities:
        if city.name.lower() in normalized or city.slug in normalized:
            results.append({"type": "city", "title": city.name, "url": city.get_absolute_url()})
            for service in services:
                service_terms = [service.name.lower(), service.slug.replace("-", " ")]
                service_tokens = [token for term in service_terms for token in term.split() if len(token) > 2]
                if any(term in normalized for term in service_terms) or any(token in normalized for token in service_tokens):
                    results.append({"type": "service", "title": service.public_label(city), "url": service.get_absolute_url(city)})

    for guide in Guide.objects.public():
        title = guide.title.lower()
        if any(token in title for token in normalized.split() if len(token) > 3):
            results.append({"type": "guide", "title": guide.title, "url": guide.get_absolute_url()})

    if include_keywords:
        tokens = [token for token in normalized.split() if len(token) > 2]
        for keyword in Keyword.objects.filter(normalized_query__icontains=tokens[0] if tokens else normalized)[:8]:
            keyword_text = keyword.normalized_query
            if all(token in keyword_text for token in tokens[:2]) or normalized in keyword_text:
                results.append({"type": "keyword", "title": keyword.query, "url": ""})

    deduped = []
    seen = set()
    for result in results:
        if result["url"] in seen:
            continue
        seen.add(result["url"])
        deduped.append(result)
    return deduped
