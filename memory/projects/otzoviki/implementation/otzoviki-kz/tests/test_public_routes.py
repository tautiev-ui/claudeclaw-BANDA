import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

from apps.companies.models import Company
from apps.qr.models import QRReviewFlow


@pytest.mark.django_db
def test_public_mvp_routes_render_with_canonical_and_breadcrumbs(client):
    routes = [
        "/kz/",
        "/kz/almaty/",
        "/kz/almaty/remont-kvartir/",
        "/kz/almaty/reyting-remontnyh-kompaniy/",
        "/kz/almaty/remont-kvartir/ceny/",
        "/kz/guides/",
        "/kz/guides/kak-proverit-kompaniyu/",
        "/methodology/",
        "/review-policy/",
        "/right-of-reply/",
        "/for-business/",
        "/claim-profile/",
        "/reputation-audit/",
    ]

    for route in routes:
        response = client.get(route)
        assert response.status_code == 200, route
        html = response.content.decode()
        assert f'<link rel="canonical" href="http://testserver{route}">' in html
        assert '"@type": "BreadcrumbList"' in html


@pytest.mark.django_db
def test_company_dossier_route_uses_country_level_canonical(client):
    Company.objects.create(name="Alma Remont", slug="alma-remont")

    response = client.get("/kz/company/alma-remont/")

    assert response.status_code == 200
    html = response.content.decode()
    assert '<link rel="canonical" href="http://testserver/kz/company/alma-remont/">' in html
    assert "Alma Remont" in html


@pytest.mark.django_db
def test_qr_token_route_is_noindex(client):
    company = Company.objects.create(name="Alma Remont", slug="alma-remont")
    flow = QRReviewFlow.objects.create(company=company, label="QR")

    response = client.get(flow.get_absolute_url())

    assert response.status_code == 200
    html = response.content.decode()
    assert '<meta name="robots" content="noindex,follow">' in html
    assert f'<link rel="canonical" href="http://testserver{flow.get_absolute_url()}">' in html


@pytest.mark.django_db
def test_submission_and_private_entry_routes_are_noindex(client):
    company = Company.objects.create(name="Alma Remont", slug="alma-remont-noindex")
    user = get_user_model().objects.create_user(username="owner", email="owner@example.com", password="pass")
    client.force_login(user)
    routes = [
        "/claim-profile/",
        "/reputation-audit/",
        f"{company.get_absolute_url()}reviews/new/",
        f"{company.get_absolute_url()}official-response/new/",
        "/business/",
        "/business/dashboard/",
    ]

    for route in routes:
        response = client.get(route)
        assert response.status_code == 200, route
        html = response.content.decode()
        assert '<meta name="robots" content="noindex,follow">' in html, route
        assert f'<link rel="canonical" href="http://testserver{route}">' in html, route
