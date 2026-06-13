import pytest
from django.core.management import call_command

from apps.services.models import Service, ServiceCategory


@pytest.mark.django_db
def test_seed_markin_services_creates_cluster_services_idempotently():
    call_command("seed_markin_services")
    call_command("seed_markin_services")

    expected_slugs = {
        "remont-kvartir",
        "stroitelstvo-domov",
        "dizayn-interera",
        "novostroyki",
        "santehnik",
        "elektrik",
        "okna-i-dveri",
    }
    assert expected_slugs.issubset(set(Service.objects.values_list("slug", flat=True)))
    assert ServiceCategory.objects.filter(slug="markin-clusters").count() == 1
    assert Service.objects.filter(slug="stroitelstvo-domov", name="Строительство домов").exists()
    assert Service.objects.filter(slug="dizayn-interera", name="Дизайн интерьера").exists()
    assert Service.objects.filter(slug="novostroyki", name="Новостройки и застройщики").exists()
