import pytest

from apps.business.models import BusinessAccount, BusinessRepresentative
from apps.companies.models import Company


@pytest.mark.django_db
def test_business_representative_permissions_require_approved_and_email_verified():
    company = Company.objects.create(name="Alma Remont", slug="alma-remont")
    account = BusinessAccount.objects.create(company=company, display_name="Alma Remont Business")

    pending = BusinessRepresentative.objects.create(account=account, full_name="Pending", email="pending@example.com")
    approved_unverified = BusinessRepresentative.objects.create(
        account=account,
        full_name="Approved",
        email="approved@example.com",
        verification_status=BusinessRepresentative.VerificationStatus.APPROVED,
        email_verified=False,
    )
    verified = BusinessRepresentative.objects.create(
        account=account,
        full_name="Verified",
        email="verified@example.com",
        verification_status=BusinessRepresentative.VerificationStatus.APPROVED,
        email_verified=True,
    )

    assert not pending.can_manage_profile
    assert not pending.can_submit_official_response
    assert not approved_unverified.can_manage_profile
    assert not approved_unverified.can_submit_official_response
    assert verified.can_manage_profile
    assert verified.can_submit_official_response


@pytest.mark.django_db
def test_business_account_verified_representatives_queryset_only_returns_verified_reps():
    company = Company.objects.create(name="Alma Remont", slug="alma-remont")
    account = BusinessAccount.objects.create(company=company, display_name="Alma Remont Business")
    BusinessRepresentative.objects.create(account=account, full_name="Pending", email="pending@example.com")
    verified = BusinessRepresentative.objects.create(
        account=account,
        full_name="Verified",
        email="verified@example.com",
        verification_status=BusinessRepresentative.VerificationStatus.APPROVED,
        email_verified=True,
    )

    assert list(account.verified_representatives()) == [verified]
    assert account.has_verified_representative
