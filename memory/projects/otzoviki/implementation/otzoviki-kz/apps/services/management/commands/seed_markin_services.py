from django.core.management.base import BaseCommand

from apps.services.models import Service, ServiceCategory


MARKIN_SERVICES = [
    ("remont-kvartir", "Ремонт квартир"),
    ("stroitelstvo-domov", "Строительство домов"),
    ("dizayn-interera", "Дизайн интерьера"),
    ("novostroyki", "Новостройки и застройщики"),
    ("santehnik", "Сантехник"),
    ("elektrik", "Электрик"),
    ("okna-i-dveri", "Окна и двери"),
]


class Command(BaseCommand):
    help = "Seed service rows required by Markin Stage 4A/4B page maps."

    def handle(self, *args, **options):
        category, _ = ServiceCategory.objects.get_or_create(
            slug="markin-clusters",
            defaults={"name": "Markin service clusters", "is_active": True},
        )
        created = 0
        updated = 0
        for slug, name in MARKIN_SERVICES:
            service, was_created = Service.objects.get_or_create(
                slug=slug,
                defaults={"category": category, "name": name, "is_active": True},
            )
            if was_created:
                created += 1
                continue
            changed = False
            if service.name != name:
                service.name = name
                changed = True
            if service.category_id != category.id:
                service.category = category
                changed = True
            if not service.is_active:
                service.is_active = True
                changed = True
            if changed:
                service.save(update_fields=["name", "category", "is_active", "updated_at"])
                updated += 1
        self.stdout.write(self.style.SUCCESS(f"Seeded Markin services: created={created}, updated={updated}, total={len(MARKIN_SERVICES)}"))
