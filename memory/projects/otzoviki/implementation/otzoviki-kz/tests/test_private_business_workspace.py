import pytest
from django.contrib.auth import get_user_model

from apps.business.models import BusinessAccount, BusinessRepresentative
from apps.companies.models import Company


@pytest.mark.django_db
def test_private_business_workspace_redirects_anonymous_to_login(client):
    for path in ["/business/", "/business/dashboard/"]:
        response = client.get(path)

        assert response.status_code == 302
        assert "/admin/login/" in response["Location"]


@pytest.mark.django_db
def test_private_business_workspace_shows_verified_representative_company_and_actions(client):
    user = get_user_model().objects.create_user(username="owner", email="owner@example.com", password="pass")
    company = Company.objects.create(name="Alma Remont", slug="alma-remont")
    account = BusinessAccount.objects.create(company=company, display_name="Alma Remont Business")
    BusinessRepresentative.objects.create(
        account=account,
        full_name="Айдар",
        email="owner@example.com",
        role_title="Директор",
        verification_status=BusinessRepresentative.VerificationStatus.APPROVED,
        email_verified=True,
    )
    client.force_login(user)

    response = client.get("/business/dashboard/")
    body = response.content.decode()

    assert response.status_code == 200
    assert '<meta name="robots" content="noindex,follow">' in body
    assert "Alma Remont" in body
    assert "Управление профилем доступно" in body
    assert f"/kz/company/{company.slug}/official-response/new/" in body
    assert "Paid profile does not affect rating" in body


@pytest.mark.django_db
def test_private_business_workspace_hides_actions_for_unverified_representative(client):
    user = get_user_model().objects.create_user(username="pending", email="pending@example.com", password="pass")
    company = Company.objects.create(name="Alma Remont", slug="alma-remont")
    account = BusinessAccount.objects.create(company=company, display_name="Alma Remont Business")
    BusinessRepresentative.objects.create(
        account=account,
        full_name="Pending",
        email="pending@example.com",
        verification_status=BusinessRepresentative.VerificationStatus.APPROVED,
        email_verified=False,
    )
    client.force_login(user)

    response = client.get("/business/dashboard/")
    body = response.content.decode()

    assert response.status_code == 200
    assert "Пока нет подтверждённых компаний" in body
    assert f"/kz/company/{company.slug}/official-response/new/" not in body
