import json

from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from apps.ai_evidence.models import AIYandexEvidenceLog
from apps.analytics.models import AnalyticsEvent, track_event
from apps.business.models import OfficialResponse
from apps.companies.models import Company, CompanyService
from apps.evidence.models import Evidence
from apps.guides.models import Guide, GuideCategory
from apps.locations.models import City
from apps.qr.models import QRReviewFlow, QRScanEvent, ReviewPlatformLink
from apps.reviews.models import RatingSnapshot, Review
from apps.services.models import Service
from apps.seo.schema import build_company_schema


PAGE_TITLES = {
    "kz_root": "Otzoviki KZ — Казахстан",
    "city_hub": "Компании и услуги в {city}",
    "city_service": "Ремонт квартир в {city}",
    "ranking": "Рейтинг ремонтных компаний в {city}",
    "price": "Цены на ремонт квартир в {city}",
    "guides": "Гайды Otzoviki KZ",
    "guide_detail": "Как проверить компанию",
    "methodology": "Методология Otzoviki KZ",
    "review_policy": "Правила отзывов",
    "right_of_reply": "Право на ответ",
    "for_business": "Для бизнеса",
    "claim_profile": "Заявить профиль",
    "reputation_audit": "Аудит репутации",
    "privacy": "Политика конфиденциальности",
    "terms": "Пользовательское соглашение",
}

PAGE_DESCRIPTIONS = {
    "privacy": "Как Otzoviki KZ обрабатывает персональные данные, заявки, отзывы, приватные доказательства и служебные события без публикации чувствительных материалов.",
    "terms": "Условия использования Otzoviki KZ: правила отзывов, модерация, право на ответ, ограничения ответственности и запрет влияния платного профиля на рейтинг.",
}


def static_page(request, page_key: str, city: str = "", slug: str = ""):
    if page_key not in PAGE_TITLES:
        raise Http404
    title = PAGE_TITLES[page_key].format(city=city.title())
    path = request.path
    return render_page(
        request,
        title=title,
        heading=title,
        description=PAGE_DESCRIPTIONS.get(page_key, "SEO-first MVP страница Otzoviki KZ с методологией, доказательствами и безопасной индексацией."),
        canonical_path=path,
        page_type=page_key,
    )


def kz_root_page(request):
    cities = City.objects.active()
    services = Service.objects.active()
    canonical_url = request.build_absolute_uri("/kz/")
    title = "Otzoviki KZ — Казахстан"
    return render(
        request,
        "pages/kz_root.html",
        {
            "cities": cities,
            "services": services,
            "page_title": title,
            "page_description": "Города Казахстана, услуги, досье компаний, отзывы, рейтинги и методология Otzoviki KZ.",
            "canonical_url": canonical_url,
            "robots_meta": "index,follow",
            "breadcrumb_json_ld": breadcrumb_json_ld(request, "Казахстан", canonical_url),
        },
    )


def city_hub_page(request, city: str):
    city_obj = City.objects.active().filter(slug=city).first()
    canonical_path = f"/kz/{city}/"
    service_url = f"/kz/{city}/remont-kvartir/"
    ranking_url = f"/kz/{city}/reyting-remontnyh-kompaniy/"
    price_url = f"/kz/{city}/remont-kvartir/ceny/"

    company_cards = []
    if city_obj:
        links = list(
            CompanyService.objects.filter(city=city_obj, company__is_active=True)
            .select_related("company")
            .order_by("company__name")
        )
        snapshots = {snapshot.company_id: snapshot for snapshot in RatingSnapshot.objects.filter(company__in=[link.company for link in links])}
        company_cards = [{"company": link.company, "snapshot": snapshots.get(link.company_id)} for link in links]
        title = f"Компании и услуги в {city_obj.name}"
        description = f"Городской хаб Otzoviki KZ для {city_obj.name}: компании, отзывы, рейтинг, цены и методология."
    else:
        city_obj = {"name": city.replace("-", " ").title(), "slug": city}
        title = f"Компании и услуги в {city_obj['name']}"
        description = "Городской хаб ожидает заполнения справочника."

    has_enough_data = bool(company_cards)
    canonical_url = request.build_absolute_uri(canonical_path)
    return render(
        request,
        "pages/city_hub.html",
        {
            "city": city_obj,
            "company_cards": company_cards,
            "service_url": service_url,
            "ranking_url": ranking_url,
            "price_url": price_url,
            "has_enough_data": has_enough_data,
            "page_title": title,
            "page_description": description,
            "canonical_url": canonical_url,
            "robots_meta": "index,follow" if has_enough_data else "noindex,follow",
            "breadcrumb_json_ld": breadcrumb_json_ld(request, title, canonical_url),
        },
    )


def city_service_page(request, city: str, service_slug: str):
    city_obj = City.objects.active().filter(slug=city).first()
    service = Service.objects.active().filter(slug=service_slug).first()
    canonical_path = f"/kz/{city}/{service_slug}/"
    ranking_url = f"/kz/{city}/reyting-remontnyh-kompaniy/"

    if city_obj and service:
        company_links = list(
            service.company_service_links.filter(city=city_obj, company__is_active=True)
            .select_related("company")
            .order_by("company__name")
        )
        companies = [link.company for link in company_links]
        snapshots = {snapshot.company_id: snapshot for snapshot in RatingSnapshot.objects.filter(company__in=companies)}
        company_cards = [{"company": link.company, "snapshot": snapshots.get(link.company_id)} for link in company_links]
        title = service.public_label(city_obj)
        description = f"Компании, отзывы и методология для услуги {service.name} в {city_obj.name}."
    else:
        company_links = []
        company_cards = []
        city_obj = {"name": city.replace("-", " ").title(), "slug": city}
        service = {"name": service_slug.replace("-", " ").title(), "slug": service_slug}
        title = f"{service['name']} в {city_obj['name']}"
        description = "Страница ожидает заполнения справочников города, услуги и компаний."

    has_enough_data = bool(company_links)
    canonical_url = request.build_absolute_uri(canonical_path)
    return render(
        request,
        "pages/city_service.html",
        {
            "city": city_obj,
            "service": service,
            "company_links": company_links,
            "company_cards": company_cards,
            "ranking_url": ranking_url,
            "has_enough_data": has_enough_data,
            "page_title": title,
            "page_description": description,
            "canonical_url": canonical_url,
            "robots_meta": "index,follow" if has_enough_data else "noindex,follow",
            "breadcrumb_json_ld": breadcrumb_json_ld(request, title, canonical_url),
        },
    )


def ranking_page(request, city: str):
    city_obj = City.objects.active().filter(slug=city).first()
    service = Service.objects.active().filter(slug="remont-kvartir").first()
    canonical_path = f"/kz/{city}/reyting-remontnyh-kompaniy/"
    service_url = f"/kz/{city}/remont-kvartir/"
    price_url = f"/kz/{city}/remont-kvartir/ceny/"

    company_cards = []
    if city_obj and service:
        links = list(
            CompanyService.objects.filter(city=city_obj, service=service, company__is_active=True)
            .select_related("company")
        )
        snapshots = {snapshot.company_id: snapshot for snapshot in RatingSnapshot.objects.filter(company__in=[link.company for link in links])}
        company_cards = sorted(
            [{"company": link.company, "snapshot": snapshots.get(link.company_id)} for link in links],
            key=lambda card: (
                card["snapshot"].average_rating if card["snapshot"] else 0,
                card["snapshot"].review_count if card["snapshot"] else 0,
                card["company"].name,
            ),
            reverse=True,
        )
        title = f"Рейтинг ремонтных компаний в {city_obj.name}"
        description = f"Рейтинг компаний по ремонту квартир в {city_obj.name}: отзывы, методология и проверяемые сигналы."
    else:
        city_obj = {"name": city.replace("-", " ").title(), "slug": city}
        title = f"Рейтинг ремонтных компаний в {city_obj['name']}"
        description = "Страница ожидает заполнения справочников и компаний."

    has_enough_data = bool(company_cards)
    canonical_url = request.build_absolute_uri(canonical_path)
    return render(
        request,
        "pages/ranking.html",
        {
            "city": city_obj,
            "company_cards": company_cards,
            "service_url": service_url,
            "price_url": price_url,
            "has_enough_data": has_enough_data,
            "page_title": title,
            "page_description": description,
            "canonical_url": canonical_url,
            "robots_meta": "index,follow" if has_enough_data else "noindex,follow",
            "breadcrumb_json_ld": breadcrumb_json_ld(request, title, canonical_url),
        },
    )


def price_page(request, city: str):
    city_obj = City.objects.active().filter(slug=city).first()
    service = Service.objects.active().filter(slug="remont-kvartir").first()
    canonical_path = f"/kz/{city}/remont-kvartir/ceny/"
    service_url = f"/kz/{city}/remont-kvartir/"
    ranking_url = f"/kz/{city}/reyting-remontnyh-kompaniy/"

    company_cards = []
    if city_obj and service:
        links = list(
            CompanyService.objects.filter(city=city_obj, service=service, company__is_active=True)
            .select_related("company")
            .order_by("company__name")
        )
        company_cards = [{"company": link.company} for link in links]
        title = f"Цены на ремонт квартир в {city_obj.name}"
        description = f"Как сравнивать цены, сметы и компании по ремонту квартир в {city_obj.name}."
    else:
        city_obj = {"name": city.replace("-", " ").title(), "slug": city}
        title = f"Цены на ремонт квартир в {city_obj['name']}"
        description = "Страница ожидает заполнения справочников и компаний."

    has_enough_data = bool(company_cards)
    canonical_url = request.build_absolute_uri(canonical_path)
    return render(
        request,
        "pages/price.html",
        {
            "city": city_obj,
            "company_cards": company_cards,
            "service_url": service_url,
            "ranking_url": ranking_url,
            "has_enough_data": has_enough_data,
            "page_title": title,
            "page_description": description,
            "canonical_url": canonical_url,
            "robots_meta": "index,follow" if has_enough_data else "noindex,follow",
            "breadcrumb_json_ld": breadcrumb_json_ld(request, title, canonical_url),
        },
    )


def guides_hub(request):
    guides = list(Guide.objects.public())
    categories = []
    for category in GuideCategory.objects.filter(is_active=True).order_by("position", "name"):
        public_guides = [guide for guide in guides if guide.category_id == category.id]
        if public_guides:
            category.public_guides = public_guides
            categories.append(category)
    canonical_url = request.build_absolute_uri("/kz/guides/")
    title = "Гайды Otzoviki KZ"
    return render(
        request,
        "pages/guides_hub.html",
        {
            "categories": categories,
            "has_guides": bool(guides),
            "page_title": title,
            "page_description": "Гайды Otzoviki KZ: проверка компаний, отзывы, сметы, договоры и право на ответ.",
            "canonical_url": canonical_url,
            "robots_meta": "index,follow" if guides else "noindex,follow",
            "breadcrumb_json_ld": breadcrumb_json_ld(request, title, canonical_url),
        },
    )


def for_business_page(request):
    canonical_url = request.build_absolute_uri("/for-business/")
    title = "Для бизнеса"
    return render(
        request,
        "pages/for_business.html",
        {
            "page_title": title,
            "page_description": "Otzoviki Business: claim profile, official response, QR review flow and reputation audit without influence on ratings.",
            "canonical_url": canonical_url,
            "robots_meta": "index,follow",
            "breadcrumb_json_ld": breadcrumb_json_ld(request, title, canonical_url),
        },
    )


def guide_detail(request, slug: str):
    guide = Guide.objects.public().filter(slug=slug).first()
    if not guide:
        if Guide.objects.filter(slug=slug).exists():
            raise Http404
        canonical_url = request.build_absolute_uri(f"/kz/guides/{slug}/")
        title = slug.replace("-", " ").title()
        return render(
            request,
            "pages/generic_page.html",
            {
                "page_title": title,
                "page_heading": title,
                "page_description": "Guide placeholder awaiting editorial content.",
                "canonical_url": canonical_url,
                "robots_meta": "noindex,follow",
                "page_type": "guide_placeholder",
                "breadcrumb_json_ld": breadcrumb_json_ld(request, title, canonical_url),
            },
        )
    canonical_url = request.build_absolute_uri(guide.get_absolute_url())
    return render(
        request,
        "pages/guide_detail.html",
        {
            "guide": guide,
            "page_title": guide.seo_title or guide.title,
            "page_description": guide.seo_description or guide.summary,
            "canonical_url": canonical_url,
            "robots_meta": guide.quality_gated_robots_meta,
            "quality_issues": guide.quality_issues,
            "breadcrumb_json_ld": breadcrumb_json_ld(request, guide.title, canonical_url),
        },
    )


def company_dossier(request, slug: str):
    company = get_object_or_404(Company, slug=slug)
    track_event(event_type=AnalyticsEvent.EventType.COMPANY_DOSSIER_OPEN, request=request, company=company)
    canonical_url = request.build_absolute_uri(company.get_absolute_url())
    company_schema = build_company_schema(request, company)
    context = {
        "page_title": f"{company.name} — досье компании",
        "page_heading": company.name,
        "page_description": company.seo_description or "Досье компании: отзывы, официальный ответ, внешний след и признаки риска.",
        "canonical_url": canonical_url,
        "robots_meta": company.robots_meta,
        "page_type": "company_dossier",
        "breadcrumb_json_ld": breadcrumb_json_ld(request, company.name, canonical_url),
        "company": company,
        "public_reviews": Review.objects.public().filter(company=company),
        "public_evidence": Evidence.objects.public().filter(company=company),
        "official_responses": OfficialResponse.objects.public().filter(company=company),
        "ai_logs": AIYandexEvidenceLog.objects.public().filter(company=company),
        "service_links": company.service_links.select_related("city", "service").order_by("city__name", "service__name"),
        "rating_snapshot": getattr(company, "rating_snapshot", None),
        "company_schema": json.dumps(company_schema, ensure_ascii=False) if company_schema else "",
    }
    return render(request, "pages/company_dossier.html", context)


def qr_landing(request, token: str):
    flow = get_object_or_404(QRReviewFlow, token=token, is_active=True)
    QRScanEvent.objects.record_scan(flow=flow, user_agent_family=request.META.get("HTTP_USER_AGENT", "")[:120])
    canonical_path = flow.get_absolute_url()
    return render(
        request,
        "pages/qr_landing.html",
        {
            "flow": flow,
            "platform_links": flow.platform_links.filter(is_active=True).order_by("platform"),
            "page_title": f"Оставить отзыв — {flow.company.name}",
            "page_heading": "Оставить отзыв без фильтрации оценки",
            "page_description": "Нейтральная QR-страница выбора площадки для отзыва.",
            "canonical_url": request.build_absolute_uri(canonical_path),
            "page_type": "qr_review_flow",
            "robots_meta": "noindex,follow",
            "breadcrumb_json_ld": breadcrumb_json_ld(request, "Оставить отзыв", request.build_absolute_uri(canonical_path)),
        },
    )


def qr_platform_click(request, token: str, platform: str):
    flow = get_object_or_404(QRReviewFlow, token=token, is_active=True)
    link = get_object_or_404(
        ReviewPlatformLink,
        flow=flow,
        platform=platform,
        is_active=True,
    )
    if not link.is_usable:
        raise Http404("QR review platform is not usable")
    link.register_click()
    return redirect(link.url)


def render_page(request, *, title: str, heading: str, description: str, canonical_path: str, page_type: str, robots: str = "index,follow", extra_context: dict | None = None):
    canonical_url = request.build_absolute_uri(canonical_path)
    context = {
        "page_title": title,
        "page_heading": heading,
        "page_description": description,
        "canonical_url": canonical_url,
        "robots_meta": robots,
        "page_type": page_type,
        "breadcrumb_json_ld": breadcrumb_json_ld(request, heading, canonical_url),
    }
    if extra_context:
        context.update(extra_context)
    return render(request, "pages/generic_page.html", context)


def breadcrumb_json_ld(request, name: str, canonical_url: str) -> str:
    return (
        '{'
        '"@context": "https://schema.org", '
        '"@type": "BreadcrumbList", '
        '"itemListElement": ['
        '{"@type": "ListItem", "position": 1, "name": "Otzoviki KZ", "item": "'
        + request.build_absolute_uri("/")
        + '"}, '
        '{"@type": "ListItem", "position": 2, "name": "'
        + name.replace('"', "'")
        + '", "item": "'
        + canonical_url
        + '"}'
        ']}'
    )
