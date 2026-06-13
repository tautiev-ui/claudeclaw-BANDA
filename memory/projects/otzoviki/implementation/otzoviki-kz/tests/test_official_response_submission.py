import pytest
from django.contrib.auth import get_user_model

from apps.business.models import BusinessAccount, BusinessRepresentative, OfficialResponse
from apps.companies.models import Company


def create_verified_representative(company, email="owner@example.com", name="Айдар"):
    account = BusinessAccount.objects.create(company=company, display_name=f"{company.name} Business")
    return BusinessRepresentative.objects.create(
        account=account,
        full_name=name,
        email=email,
        role_title="Директор",
        verification_status=BusinessRepresentative.VerificationStatus.APPROVED,
        email_verified=True,
    )


@pytest.mark.django_db
def test_official_response_form_links_right_of_reply_policy(client):
    company = Company.objects.create(name="Alma Remont", slug="alma-remont")

    response = client.get(f"/kz/company/{company.slug}/official-response/new/")

    assert response.status_code == 200
    html = response.content.decode()
    assert "Право на ответ" in html
    assert "/right-of-reply/" in html
    assert "официальный ответ отделён" in html.lower()


@pytest.mark.django_db
def test_official_response_form_prefills_verified_representative_identity(client):
    user = get_user_model().objects.create_user(username="owner", email="owner@example.com", password="pass")
    company = Company.objects.create(name="Alma Remont", slug="alma-remont")
    create_verified_representative(company)
    client.force_login(user)

    response = client.get(f"/kz/company/{company.slug}/official-response/new/")
    html = response.content.decode()

    assert response.status_code == 200
    assert 'value="Айдар"' in html
    assert 'value="owner@example.com"' in html
    assert 'value="Директор"' in html
    assert "Подтверждённый представитель определяется по вашему аккаунту" in html


@pytest.mark.django_db
def test_official_response_submission_creates_pending_response_and_representative(client):
    company = Company.objects.create(name="Alma Remont", slug="alma-remont")

    response = client.post(
        f"/kz/company/{company.slug}/official-response/new/",
        {
            "contact_name": "Айдар",
            "contact_email": "owner@example.com",
            "role_title": "Директор",
            "body": "Готовы предоставить договор, акты и гарантийные документы.",
        },
    )

    assert response.status_code == 302
    official_response = OfficialResponse.objects.get(company=company)
    representative = BusinessRepresentative.objects.get(email="owner@example.com")
    assert official_response.status == OfficialResponse.Status.PENDING
    assert official_response.published_at is None
    assert official_response.representative == representative
    assert OfficialResponse.objects.public().count() == 0


@pytest.mark.django_db
def test_anonymous_official_response_submission_does_not_spoof_existing_verified_representative(client):
    company = Company.objects.create(name="Alma Remont", slug="alma-remont")
    account = BusinessAccount.objects.create(company=company, display_name="Alma Remont Business")
    verified = BusinessRepresentative.objects.create(
        account=account,
        full_name="Айдар",
        email="owner@example.com",
        verification_status=BusinessRepresentative.VerificationStatus.APPROVED,
        email_verified=True,
    )

    response = client.post(
        f"/kz/company/{company.slug}/official-response/new/",
        {
            "contact_name": "Spoofer",
            "contact_email": "owner@example.com",
            "role_title": "Fake director",
            "body": "Пытаюсь выдать себя за владельца.",
        },
    )

    assert response.status_code == 302
    official_response = OfficialResponse.objects.get(company=company)
    verified.refresh_from_db()
    assert official_response.status == OfficialResponse.Status.PENDING
    assert official_response.representative is None
    assert verified.full_name == "Айдар"
    assert verified.is_verified


@pytest.mark.django_db
def test_authenticated_verified_representative_submission_links_existing_representative(client):
    user = get_user_model().objects.create_user(username="owner", email="owner@example.com", password="pass")
    company = Company.objects.create(name="Alma Remont", slug="alma-remont")
    account = BusinessAccount.objects.create(company=company, display_name="Alma Remont Business")
    verified = BusinessRepresentative.objects.create(
        account=account,
        full_name="Айдар",
        email="owner@example.com",
        verification_status=BusinessRepresentative.VerificationStatus.APPROVED,
        email_verified=True,
    )
    client.force_login(user)

    response = client.post(
        f"/kz/company/{company.slug}/official-response/new/",
        {
            "contact_name": "Айдар",
            "contact_email": "owner@example.com",
            "role_title": "Директор",
            "body": "Официально готовы предоставить документы.",
        },
    )

    assert response.status_code == 302
    official_response = OfficialResponse.objects.get(company=company)
    assert official_response.representative == verified
    assert official_response.status == OfficialResponse.Status.PENDING


@pytest.mark.django_db
def test_authenticated_verified_representative_submission_ignores_posted_email_spoof(client):
    user = get_user_model().objects.create_user(username="owner", email="owner@example.com", password="pass")
    company = Company.objects.create(name="Alma Remont", slug="alma-remont")
    account = BusinessAccount.objects.create(company=company, display_name="Alma Remont Business")
    verified = BusinessRepresentative.objects.create(
        account=account,
        full_name="Айдар",
        email="owner@example.com",
        verification_status=BusinessRepresentative.VerificationStatus.APPROVED,
        email_verified=True,
    )
    client.force_login(user)

    response = client.post(
        f"/kz/company/{company.slug}/official-response/new/",
        {
            "contact_name": "Mallory",
            "contact_email": "mallory@example.com",
            "role_title": "Fake role",
            "body": "Официальный ответ должен идти от залогиненного представителя, не из POST email.",
        },
    )

    assert response.status_code == 302
    official_response = OfficialResponse.objects.get(company=company)
    assert official_response.representative == verified
    assert not BusinessRepresentative.objects.filter(email="mallory@example.com").exists()
