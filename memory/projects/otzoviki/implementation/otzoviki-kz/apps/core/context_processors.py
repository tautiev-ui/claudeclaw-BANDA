from apps.locations.models import City


PUBLIC_ROUTE_LABELS = {
    "kz": "Казахстан",
    "guides": "Гайды",
    "almaty": "Алматы",
    "astana": "Астана",
    "remont-kvartir": "Ремонт квартир",
    "reyting-remontnyh-kompaniy": "Рейтинг компаний",
    "ceny": "Цены",
    "company": "Компании",
    "search": "Поиск",
    "claim-profile": "Заявить профиль",
    "reputation-audit": "Аудит репутации",
    "methodology": "Методология",
    "review-policy": "Правила отзывов",
    "right-of-reply": "Право на ответ",
    "for-business": "Для компаний",
}


PUBLIC_ROUTE_BACKS = {
    "/": ("/", "Назад к началу"),
    "/kz/": ("/", "Назад на главную"),
    "/kz/almaty/": ("/kz/", "Назад к городам"),
    "/kz/astana/": ("/kz/", "Назад к городам"),
    "/kz/almaty/remont-kvartir/": ("/kz/almaty/", "Назад к Алматы"),
    "/kz/astana/remont-kvartir/": ("/kz/astana/", "Назад к Астане"),
    "/kz/almaty/reyting-remontnyh-kompaniy/": ("/kz/almaty/remont-kvartir/", "Назад к компаниям"),
    "/kz/astana/reyting-remontnyh-kompaniy/": ("/kz/astana/remont-kvartir/", "Назад к компаниям"),
    "/kz/almaty/remont-kvartir/ceny/": ("/kz/almaty/remont-kvartir/", "Назад к ремонту квартир"),
    "/kz/astana/remont-kvartir/ceny/": ("/kz/astana/remont-kvartir/", "Назад к ремонту квартир"),
    "/kz/guides/": ("/kz/", "Назад к Казахстану"),
    "/search/": ("/", "Назад на главную"),
    "/claim-profile/": ("/", "Назад на главную"),
    "/reputation-audit/": ("/for-business/", "Назад для компаний"),
}


def city_selector(request):
    return {"city_selector_cities": City.objects.active()[:12]}


def public_navigation(request):
    path = request.path if request.path.endswith("/") else f"{request.path}/"
    crumbs = [{"label": "Главная", "url": "/"}]
    if path != "/":
        parts = [part for part in path.strip("/").split("/") if part]
        built = ""
        for index, part in enumerate(parts):
            built += f"/{part}"
            url = f"{built}/"
            if index == len(parts) - 1:
                label = PUBLIC_ROUTE_LABELS.get(part, part.replace("-", " ").title())
            else:
                label = PUBLIC_ROUTE_LABELS.get(part, part.replace("-", " ").title())
            crumbs.append({"label": label, "url": url})
    back_url, back_label = PUBLIC_ROUTE_BACKS.get(path, (crumbs[-2]["url"] if len(crumbs) > 1 else "/", "Назад"))
    return {
        "visible_breadcrumbs": crumbs,
        "back_url": back_url,
        "back_label": back_label,
    }
