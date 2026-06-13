import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.companies.models import Company
from apps.seo.indexability import IndexabilityStatus


@pytest.mark.django_db
def test_company_cannot_be_marked_indexable_without_required_seo_and_trust_fields():
    company = Company(
        name="Empty Remont",
        slug="empty-remont",
        index_status=IndexabilityStatus.INDEXABLE,
        seo_title="",
        seo_description="",
        source_count=0,
        last_verified_at=None,
        methodology_version="",
    )

    with pytest.raises(ValidationError) as exc:
        company.full_clean()

    errors = exc.value.message_dict
    assert "index_status" in errors
    message = " ".join(errors["index_status"])
    assert "seo_title" in message
    assert "seo_description" in message
    assert "source_count" in message
    assert "last_verified_at" in message
    assert "methodology_version" in message


@pytest.mark.django_db
def test_company_indexable_validation_allows_filled_dossier():
    company = Company(
        name="Filled Remont",
        slug="filled-remont",
        index_status=IndexabilityStatus.INDEXABLE,
        seo_title="Filled Remont отзывы",
        seo_description="Заполненное досье компании.",
        source_count=2,
        last_verified_at=timezone.now(),
        methodology_version="2026.1",
    )

    company.full_clean()
