import pytest
from django.contrib.auth import get_user_model

from apps.business.models import BusinessAccount, BusinessRepresentative, OfficialResponse
from apps.companies.models import Company


def create_account(company_name="Alma Remont", slug="alma-remont"):
    company = Company.objects.create(name=company_name, slug=slug)
    account = BusinessAccount.objects.create(company=company, display_name=f"{company_name} Business")
    return company, account


@pytest.mark.django_db
def test_business_workspace_70_gate_verified_dashboard(client):
    user = get_user_model().objects.create_user(username="owner", email="owner@example.com", password="pass")
    company, account = create_account()
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
    html = response.content.decode()

    assert response.status_code == 200
    markers = [
        '<meta name="robots" content="noindex,follow">',
        '<link rel="canonical" href="http://testserver/business/dashboard/">',
        "70-gate private B2B workspace",
        "Private workspace",
        "Business dashboard",
        "Identity source: logged-in account email",
        "owner@example.com",
        "Verified representative",
        "Айдар",
        "Директор",
        "Company management permissions",
        "can_manage_profile: yes",
        "can_submit_official_response: yes",
        "Managed companies",
        "Alma Remont",
        company.get_absolute_url(),
        f"{company.get_absolute_url()}official-response/new/",
        "Управление профилем доступно",
        "Подать официальный ответ",
        "Right-of-reply workflow",
        "/right-of-reply/",
        "Claim/profile changes remain moderated",
        "/claim-profile/",
        "Reputation audit",
        "/reputation-audit/",
        "Paid profile does not affect rating",
        "ranking, reviews, indexability, or editorial conclusions",
        "No review deletion privilege",
        "No rating override privilege",
        "No schema/indexing override privilege",
        "Public dossier remains canonical",
        "Official responses publish only after moderation",
        "Private business data is not public evidence",
        "noindex private workspace",
        "Audit-friendly identity resolution",
    ]
    for marker in markers:
        assert marker in html, marker


@pytest.mark.django_db
def test_business_workspace_70_gate_pending_unverified_dashboard(client):
    user = get_user_model().objects.create_user(username="pending", email="pending@example.com", password="pass")
    company, account = create_account()
    BusinessRepresentative.objects.create(
        account=account,
        full_name="Pending Person",
        email="pending@example.com",
        role_title="Маркетолог",
        verification_status=BusinessRepresentative.VerificationStatus.PENDING,
        email_verified=False,
    )
    client.force_login(user)

    response = client.get("/business/dashboard/")
    html = response.content.decode()

    assert response.status_code == 200
    markers = [
        "Пока нет подтверждённых компаний",
        "Verification required",
        "Pending representative",
        "Pending Person",
        "Маркетолог",
        "verification_status: pending",
        "email_verified: no",
        "can_manage_profile: no",
        "can_submit_official_response: no",
        "Actions hidden until approval and email verification",
        "Official response action hidden",
        "Profile management action hidden",
        "Заявите профиль",
        "дождитесь проверки email",
        "Без подтверждения действия управления",
        "/claim-profile/",
        "/reputation-audit/",
        "Paid profile does not affect rating",
        "No review deletion privilege",
        "No rating override privilege",
    ]
    for marker in markers:
        assert marker in html, marker
    assert f"{company.get_absolute_url()}official-response/new/" not in html


@pytest.mark.django_db
def test_official_response_form_70_gate_identity_and_policy_copy(client):
    user = get_user_model().objects.create_user(username="owner", email="owner@example.com", password="pass")
    company, account = create_account()
    BusinessRepresentative.objects.create(
        account=account,
        full_name="Айдар",
        email="owner@example.com",
        role_title="Директор",
        verification_status=BusinessRepresentative.VerificationStatus.APPROVED,
        email_verified=True,
    )
    client.force_login(user)

    response = client.get(f"{company.get_absolute_url()}official-response/new/")
    html = response.content.decode()

    assert response.status_code == 200
    markers = [
        '<meta name="robots" content="noindex,follow">',
        f'<link rel="canonical" href="http://testserver{company.get_absolute_url()}official-response/new/">',
        "70-gate official response identity safety",
        "Официальный ответ для Alma Remont",
        "right of reply",
        "/right-of-reply/",
        "Подтверждённый представитель определяется по вашему аккаунту",
        "Identity source: authenticated account, not editable POST identity",
        "Айдар",
        "owner@example.com",
        "Директор",
        'value="Айдар"',
        'value="owner@example.com"',
        'value="Директор"',
        "Verified representative status: approved + email verified",
        "POST contact email cannot claim another verified representative",
        "Anonymous submissions cannot attach to existing verified representative by email",
        "Submitted response starts pending",
        "Moderation required before publication",
        "Official response is separate from reviews and rating",
        "Paid profile does not affect rating",
        "No deletion of reviews",
        "No ranking boost",
        "Private proof is not rendered publicly",
        "source_page uses same-host attribution",
    ]
    for marker in markers:
        assert marker in html, marker


@pytest.mark.django_db
def test_official_response_70_gate_post_identity_safety(client):
    user = get_user_model().objects.create_user(username="owner", email="owner@example.com", password="pass")
    company, account = create_account()
    verified = BusinessRepresentative.objects.create(
        account=account,
        full_name="Айдар",
        email="owner@example.com",
        role_title="Директор",
        verification_status=BusinessRepresentative.VerificationStatus.APPROVED,
        email_verified=True,
    )
    client.force_login(user)

    response = client.post(
        f"{company.get_absolute_url()}official-response/new/",
        {
            "contact_name": "Mallory",
            "contact_email": "mallory@example.com",
            "role_title": "Fake role",
            "body": "POST identity must not override the authenticated verified representative.",
        },
        HTTP_REFERER=f"http://testserver{company.get_absolute_url()}?utm=secret#frag",
    )

    assert response.status_code == 302
    official_response = OfficialResponse.objects.get(company=company)
    assert official_response.representative == verified
    assert official_response.status == OfficialResponse.Status.PENDING
    assert official_response.source_page == company.get_absolute_url()
    assert not BusinessRepresentative.objects.filter(email="mallory@example.com").exists()

    anonymous = client.__class__()
    response = anonymous.post(
        f"{company.get_absolute_url()}official-response/new/",
        {
            "contact_name": "Spoofer",
            "contact_email": "owner@example.com",
            "role_title": "Fake director",
            "body": "Anonymous spoof should not attach to verified rep.",
        },
    )
    assert response.status_code == 302
    spoofed_response = OfficialResponse.objects.order_by("-id").first()
    assert spoofed_response.representative is None


@pytest.mark.django_db
def test_business_workspace_routes_70_gate_anonymous_redirects(client):
    for path in ["/business/", "/business/dashboard/", "/business/profile/", "/business/responses/"]:
        response = client.get(path)
        assert response.status_code == 302
        assert "/admin/login/" in response["Location"]
