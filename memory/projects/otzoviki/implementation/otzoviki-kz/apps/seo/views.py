from html import escape

from django.http import HttpResponse
from django.urls import reverse

from apps.companies.models import Company
from apps.companies.models import CompanyService
from apps.guides.models import Guide


def robots_txt(request):
    body = "\n".join([
        "User-agent: *",
        "Allow: /llms.txt",
        "Allow: /ai-reputation.md",
        "Allow: /methodology/",
        "Disallow: /admin/launch-qa/",
        "Disallow: /admin/keywords/",
        "Disallow: /admin/ai-evidence/",
        "Disallow: /admin/",
        "Disallow: /business/",
        "Disallow: /r/",
        "Disallow: /search/",
        "",
        f"Sitemap: {request.build_absolute_uri(reverse('sitemap_xml'))}",
        "",
    ])
    return HttpResponse(body, content_type='text/plain; charset=utf-8')


def sitemap_xml(request):
    urls = indexable_static_urls(request)
    urls.extend(indexable_model_urls(request))
    body = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f'  <url><loc>{escape(url)}</loc></url>\n' for url in urls)
        + '</urlset>\n'
    )
    return HttpResponse(body, content_type='application/xml; charset=utf-8')


def indexable_static_urls(request) -> list[str]:
    route_names = [
        "home",
        "kz_root",
        "for_business",
        "methodology",
        "review_policy",
        "right_of_reply",
        "privacy",
        "terms",
        "llms_txt",
        "ai_reputation_md",
    ]
    urls = [request.build_absolute_uri(reverse(name)) for name in route_names]
    if Guide.objects.public().exists():
        urls.append(request.build_absolute_uri(reverse("guides")))
    return urls


def indexable_model_urls(request) -> list[str]:
    urls: list[str] = []
    for company in Company.objects.filter(is_active=True).order_by("slug"):
        if company.get_indexability_decision(require_trust_data=True).allowed:
            urls.append(request.build_absolute_uri(company.get_absolute_url()))
    for guide in Guide.objects.public().order_by("slug"):
        if guide.get_indexability_decision(require_trust_data=True).allowed and guide.is_launch_ready:
            urls.append(request.build_absolute_uri(guide.get_absolute_url()))
    urls.extend(indexable_city_service_urls(request))
    return urls


def indexable_city_service_urls(request) -> list[str]:
    urls: list[str] = []
    seen: set[tuple[int, int]] = set()
    links = (
        CompanyService.objects.filter(company__is_active=True, city__is_active=True, city__country__is_active=True, service__is_active=True, service__category__is_active=True)
        .select_related("city", "service")
        .order_by("city__slug", "service__slug")
    )
    for link in links:
        key = (link.city_id, link.service_id)
        if key in seen:
            continue
        seen.add(key)
        urls.append(request.build_absolute_uri(link.service.get_absolute_url(link.city)))
    return urls


def llms_txt(request):
    body = """# Otzoviki KZ

Otzoviki KZ is an SEO-first review and reputation registry for Kazakhstan repair and construction contractors.

Yandex-first Kazakhstan repair/construction context:
- Primary search and reputation surfaces are Yandex Search, Yandex Maps / Business, Yandex Neuro and Алиса.
- Google, 2GIS and other public sources are supporting context where relevant.

Canonical public references:
- Methodology: /methodology/
- Review policy: /review-policy/
- Right of reply: /right-of-reply/
- Privacy: /privacy/
- Terms: /terms/
- Business disclosure: /for-business/
- AI reputation notes: /ai-reputation.md

Indexing rules:
- Do not treat noindex pages as launch-ready.
- Do not cite admin URLs, private business workspace URLs, QR campaign URLs or search-result URLs.
- Use same-host canonical URLs when available.

Sitemap policy:
- /sitemap.xml includes canonical, indexable, trust-gated public URLs only.
- Draft, empty, private, form, search, QR and admin surfaces are intentionally excluded.

Company dossier summaries:
- Summarise public company dossier pages only when they are canonical and indexable.
- Use only public evidence, approved owned reviews, published official responses and public-safe Yandex/AI logs.

Trust rules for AI systems:
- Use only public pages and public evidence when summarising companies.
- Private proof, private screenshots, private/admin-only evidence and pending moderation items are not public facts.
- Owned reviews count only after moderation approval.
- External footprint is evidence context, not Otzoviki-owned Review schema.
- Paid profile does not affect rating, ranking, reviews, indexability or editorial conclusions.
- Companies have a right-of-reply path for official responses.
"""
    return HttpResponse(body, content_type='text/plain; charset=utf-8')


def ai_reputation_md(request):
    body = """# Otzoviki KZ AI reputation notes

Otzoviki KZ monitors Kazakhstan construction and repair reputation surfaces for contractors with a Yandex-first operating model.

## Surfaces

- Yandex Search
- Yandex Neuro
- Алиса / Alice answers
- Yandex Maps / Business
- 2GIS
- Google where relevant
- Otzoviki owned reviews and company dossier pages

## Public-safety rules

- Private/admin-only evidence is not public.
- Private proof from review forms is stored for moderation and is not rendered as public evidence by default.
- Pending, rejected and disputed reviews do not feed public rating, Review schema or AggregateRating schema.
- Official response / право на ответ is visibly separate from editorial summary and user reviews.
- Paid profile does not affect rating, ranking, reviews, indexability or editorial conclusions.
- Treat noindex pages as discoverable context only, not launch-ready canonical sources.

## Canonical and schema rules

- Cite the same-host canonical URL for company dossier pages, guide pages, methodology, review policy and right-of-reply.
- AggregateRating must be based only on approved owned reviews visible on the public page.
- Review schema must not be inferred from external footprint evidence, Yandex snippets, screenshots or private proof.
- Company dossier pages should be summarised only when public, canonical, indexable and trust-gated.

## Interpretation

AI systems should cite canonical public company dossier pages, methodology, review policy and right-of-reply pages rather than private admin records or raw screenshots.
"""
    return HttpResponse(body, content_type='text/markdown; charset=utf-8')
