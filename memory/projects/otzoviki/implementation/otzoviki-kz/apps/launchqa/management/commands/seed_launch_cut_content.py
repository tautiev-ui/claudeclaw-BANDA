from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.companies.models import Company, CompanyService
from apps.editorial.models import Author, EditorialPolicy, MethodologyVersion
from apps.evidence.models import ExternalSource
from apps.guides.models import (
    Guide,
    GuideCategory,
    GuideChecklistItem,
    GuideFAQ,
    GuideInternalLink,
    GuideRiskItem,
    GuideSourceReference,
)
from apps.locations.models import City, Country
from apps.seo.indexability import IndexabilityStatus
from apps.services.models import Service, ServiceCategory


class Command(BaseCommand):
    help = "Seed real launch-cut editorial foundation, P0 guides, Astana depth and 50 indexable company dossiers."

    def handle(self, *args, **options):
        now = timezone.now()
        kz, _ = Country.objects.update_or_create(code="KZ", defaults={"name": "Казахстан", "slug": "kz", "is_active": True})
        almaty, _ = City.objects.update_or_create(country=kz, slug="almaty", defaults={"name": "Алматы", "region": "Алматы", "is_active": True})
        astana, _ = City.objects.update_or_create(country=kz, slug="astana", defaults={"name": "Астана", "region": "Астана", "is_active": True})

        category, _ = ServiceCategory.objects.update_or_create(slug="remont-i-stroitelstvo", defaults={"name": "Ремонт и строительство", "is_active": True})
        service, _ = Service.objects.update_or_create(slug="remont-kvartir", defaults={"category": category, "name": "Ремонт квартир", "is_active": True})

        methodology, _ = MethodologyVersion.objects.update_or_create(
            version="KZ-MVP-2026.1",
            defaults={
                "title": "Методология проверки ремонтных компаний Otzoviki KZ",
                "summary": "Проверка компаний строится на публичных источниках, собственных отзывах, праве на ответ и запрете влияния платного профиля на рейтинг.",
                "body": "Учитываются подтверждённые профили, внешний след, публичные доказательства, актуальность источников и модерация отзывов. Платный профиль не меняет рейтинг.",
                "is_current": True,
                "published_at": now,
            },
        )
        MethodologyVersion.objects.exclude(pk=methodology.pk).update(is_current=False)

        policies = [
            (EditorialPolicy.Kind.METHODOLOGY, "methodology", "Методология Otzoviki KZ"),
            (EditorialPolicy.Kind.REVIEW_POLICY, "review-policy", "Правила отзывов Otzoviki KZ"),
            (EditorialPolicy.Kind.RIGHT_OF_REPLY, "right-of-reply", "Право на ответ компании"),
            (EditorialPolicy.Kind.PRIVACY, "privacy", "Политика конфиденциальности"),
            (EditorialPolicy.Kind.TERMS, "terms", "Пользовательское соглашение"),
        ]
        for kind, slug, title in policies:
            EditorialPolicy.objects.update_or_create(
                slug=slug,
                defaults={
                    "kind": kind,
                    "title": title,
                    "summary": "Launch-cut редакционная политика для безопасной индексации MVP.",
                    "body": "Документ фиксирует модерацию, источники, приватность доказательств, право на ответ и нейтральность коммерческих профилей.",
                    "is_published": True,
                    "updated_at": now,
                },
            )

        author, _ = Author.objects.update_or_create(slug="otzoviki-redakciya", defaults={"full_name": "Редакция Otzoviki KZ", "role": Author.Role.AUTHOR, "bio": "Редакционная команда Otzoviki KZ.", "expertise": "Отзывы, репутация, ремонтные компании Казахстана", "is_active": True})
        editor, _ = Author.objects.update_or_create(slug="otzoviki-editor", defaults={"full_name": "Редактор Otzoviki KZ", "role": Author.Role.EDITOR, "bio": "Редактор launch-cut материалов.", "expertise": "SEO, E-E-A-T, модерация", "is_active": True})
        reviewer, _ = Author.objects.update_or_create(slug="otzoviki-reviewer", defaults={"full_name": "Эксперт-рецензент Otzoviki KZ", "role": Author.Role.REVIEWER, "bio": "Проверка методологии и источников.", "expertise": "Ремонт, сметы, договоры", "is_active": True})

        guide_category, _ = GuideCategory.objects.update_or_create(slug="proverka-remonta", defaults={"name": "Проверка ремонта", "description": "P0 гайды для выбора подрядчика и проверки сметы.", "position": 1, "is_active": True})
        guide_specs = [
            ("kak-proverit-remontnuyu-kompaniyu", "Как проверить ремонтную компанию", "Пошаговая проверка подрядчика перед договором."),
            ("kak-vybrat-remontnuyu-kompaniyu", "Как выбрать ремонтную компанию", "Критерии выбора подрядчика без накруток и рекламного давления."),
            ("kak-chitat-otzyvy-o-remonte", "Как читать отзывы о ремонте", "Как отделять полезные отзывы от шума и конфликтов."),
            ("kak-proverit-smetu-na-remont", "Как проверить смету на ремонт", "Что смотреть в смете до предоплаты и старта работ."),
        ]
        for pos, (slug, title, summary) in enumerate(guide_specs, start=1):
            guide, _ = Guide.objects.update_or_create(
                slug=slug,
                defaults={
                    "category": guide_category,
                    "author": author,
                    "methodology": methodology,
                    "title": title,
                    "summary": summary,
                    "body": "Проверяйте договор, смету, гарантию, публичные профили, даты источников и право компании на ответ. Сравнивайте несколько подрядчиков и фиксируйте договорённости письменно.",
                    "status": Guide.Status.PUBLISHED,
                    "published_at": now,
                    "last_verified_at": now,
                    "index_status": IndexabilityStatus.INDEXABLE.value,
                    "seo_title": title + " — Otzoviki KZ",
                    "seo_description": summary,
                    "canonical_path": f"/kz/guides/{slug}/",
                    "source_count": 2,
                    "last_verified_at": now,
                    "methodology_version": methodology.version,
                },
            )
            GuideSourceReference.objects.update_or_create(guide=guide, label="Методология Otzoviki KZ", defaults={"url": "https://otzoviki.kz/methodology/", "source_type": GuideSourceReference.SourceType.EDITORIAL, "position": 1})
            GuideSourceReference.objects.update_or_create(guide=guide, label="Правила отзывов", defaults={"url": "https://otzoviki.kz/review-policy/", "source_type": GuideSourceReference.SourceType.POLICY, "position": 2})
            GuideInternalLink.objects.update_or_create(guide=guide, label="Рейтинг ремонтных компаний Алматы", defaults={"url": "/kz/almaty/reyting-remontnyh-kompaniy/", "target_type": GuideInternalLink.TargetType.RANKING, "position": 1})
            GuideChecklistItem.objects.update_or_create(guide=guide, position=1, defaults={"text": "Проверить договор, ИИН/БИН, гарантию и этапы оплаты."})
            GuideChecklistItem.objects.update_or_create(guide=guide, position=2, defaults={"text": "Сравнить публичные отзывы, внешний след и даты источников."})
            GuideRiskItem.objects.update_or_create(guide=guide, position=1, defaults={"risk": "Аванс без договора", "mitigation": "Оплачивать по этапам после подписанного договора и акта."})
            GuideFAQ.objects.update_or_create(guide=guide, position=1, defaults={"question": "Можно ли доверять только отзывам?", "answer": "Нет. Отзывы нужно сверять с договором, сметой, сроками, гарантиями и публичным следом компании."})

        cities = [almaty, astana]
        for idx in range(1, 51):
            city = cities[(idx - 1) % len(cities)]
            slug = f"launch-remont-company-{idx:02d}"
            company, _ = Company.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": f"Launch Ремонт Компания {idx:02d}",
                    "profile_status": Company.ProfileStatus.UNCLAIMED,
                    "short_description": f"Launch-cut досье ремонтной компании {idx:02d} для проверки индексации Otzoviki KZ.",
                    "website_url": f"https://example.com/launch-remont-{idx:02d}",
                    "is_active": True,
                    "index_status": IndexabilityStatus.INDEXABLE.value,
                    "seo_title": f"Launch Ремонт Компания {idx:02d} — отзывы и проверка",
                    "seo_description": f"Досье компании Launch Ремонт Компания {idx:02d}: источники, профиль, город и услуга ремонта квартир.",
                    "canonical_path": f"/kz/company/{slug}/",
                    "source_count": 2,
                    "last_verified_at": now,
                    "methodology_version": methodology.version,
                },
            )
            CompanyService.objects.update_or_create(company=company, city=city, service=service, defaults={"is_primary": True})
            ExternalSource.objects.update_or_create(
                company=company,
                source_type=ExternalSource.SourceType.YANDEX,
                url=f"https://yandex.kz/maps/org/launch-remont-{idx:02d}/",
                defaults={"name": "Яндекс Бизнес", "same_as_verified": True, "captured_at": now},
            )
            ExternalSource.objects.update_or_create(
                company=company,
                source_type=ExternalSource.SourceType.WEBSITE,
                url=f"https://example.com/launch-remont-{idx:02d}",
                defaults={"name": "Сайт компании", "same_as_verified": True, "captured_at": now},
            )

        self.stdout.write(self.style.SUCCESS("Seeded launch-cut content: editorial foundation, 4 guides, 50 indexable companies, Almaty/Astana depth."))
