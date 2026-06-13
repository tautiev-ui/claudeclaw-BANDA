from django.core.management.base import BaseCommand

from apps.keywords.models import KeywordCluster, KeywordPageMap

NEXT_WAVE = [
    ("markin-next-astana-remont-kvartir", "Астана ремонт квартир", KeywordCluster.Intent.COMMERCIAL, KeywordPageMap.PageType.CITY_SERVICE, "/kz/{city}/remont-kvartir/", KeywordPageMap.Priority.P0, True, "Build/verify city-service template with Markin blocks and local proof."),
    ("markin-next-almaty-remont-kvartir", "Алматы ремонт квартир", KeywordCluster.Intent.COMMERCIAL, KeywordPageMap.PageType.CITY_SERVICE, "/kz/{city}/remont-kvartir/", KeywordPageMap.Priority.P0, True, "Expand Almaty city-service copy and proof blocks."),
    ("markin-next-astana-rating", "Астана рейтинг ремонтных компаний", KeywordCluster.Intent.COMMERCIAL, KeywordPageMap.PageType.RANKING, "/kz/{city}/reyting-remontnyh-kompaniy/", KeywordPageMap.Priority.P0, True, "Ranking page: methodology, comparison, visible ItemList data."),
    ("markin-next-almaty-rating", "Алматы рейтинг ремонтных компаний", KeywordCluster.Intent.COMMERCIAL, KeywordPageMap.PageType.RANKING, "/kz/{city}/reyting-remontnyh-kompaniy/", KeywordPageMap.Priority.P0, True, "Ranking page: methodology, comparison, visible ItemList data."),
    ("markin-next-remont-price", "цены на ремонт квартир Казахстан", KeywordCluster.Intent.COMMERCIAL, KeywordPageMap.PageType.PRICE, "/kz/{city}/remont-kvartir/ceny/", KeywordPageMap.Priority.P0, True, "Price/smeta page with ranges, caveats and conversion to company dossiers."),
    ("markin-next-company-reviews", "бренд отзывы жалобы рейтинг", KeywordCluster.Intent.NAVIGATIONAL, KeywordPageMap.PageType.COMPANY_DOSSIER, "/kz/company/{slug}/", KeywordPageMap.Priority.P0, True, "Company reputation dossier template for brand+reviews/complaints/rating queries."),
    ("markin-next-check-contractor-guide", "как проверить подрядчика перед договором", KeywordCluster.Intent.INFORMATIONAL, KeywordPageMap.PageType.GUIDE, "/kz/guides/kak-proverit-remontnuyu-kompaniyu/", KeywordPageMap.Priority.P0, True, "P0 guide supports city/ranking/company pages."),
    ("markin-next-smeta-guide", "как проверить смету на ремонт", KeywordCluster.Intent.INFORMATIONAL, KeywordPageMap.PageType.GUIDE, "/kz/guides/kak-proverit-smetu-na-remont/", KeywordPageMap.Priority.P1, True, "Guide prototype for price/smeta intent."),
    ("markin-next-yandex-reviews", "яндекс отзывы ремонтная компания", KeywordCluster.Intent.MIXED, KeywordPageMap.PageType.COMPANY_DOSSIER, "/kz/company/{slug}/", KeywordPageMap.Priority.P1, True, "Yandex/2GIS evidence block for company dossiers."),
    ("markin-next-business-reputation-audit", "аудит репутации строительной компании", KeywordCluster.Intent.COMMERCIAL, KeywordPageMap.PageType.OTHER, "/reputation-audit/", KeywordPageMap.Priority.P1, False, "B2B lead page stays noindex until paid/service copy and compliance review are ready."),
    ("markin-next-right-of-reply", "официальный ответ компании на отзыв", KeywordCluster.Intent.MIXED, KeywordPageMap.PageType.OTHER, "/right-of-reply/", KeywordPageMap.Priority.P1, True, "Trust/legal support page for dossier and B2B flows."),
    ("markin-next-guides-hub", "гайды по выбору ремонтной компании", KeywordCluster.Intent.INFORMATIONAL, KeywordPageMap.PageType.GUIDE, "/kz/guides/", KeywordPageMap.Priority.P1, True, "Guides hub must carry content SERP map, internal links and freshness."),
]


class Command(BaseCommand):
    help = "Seed Markin next-wave semantic page maps for post-launch expansion queue."

    def handle(self, *args, **options):
        created = 0
        for slug, name, intent, page_type, pattern, priority, indexable, notes in NEXT_WAVE:
            cluster, _ = KeywordCluster.objects.update_or_create(
                slug=slug,
                defaults={"name": name, "intent": intent, "page_type": page_type},
            )
            _, was_created = KeywordPageMap.objects.update_or_create(
                cluster=cluster,
                page_type=page_type,
                canonical_pattern=pattern,
                defaults={"priority": priority, "is_indexable_candidate": indexable, "notes": notes},
            )
            created += 1 if was_created else 0
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(NEXT_WAVE)} Markin next-wave page maps ({created} new)."))
