import pytest
from django.core.exceptions import ValidationError

from apps.companies.models import Company
from apps.reviews.models import RatingSnapshot, Review


@pytest.mark.django_db
def test_approved_reviews_are_public_and_have_average_rating():
    company = Company.objects.create(name="Alma Remont", slug="alma-remont")
    approved = Review.objects.create(
        company=company,
        author_name="Клиент",
        title="Сделали ремонт",
        body="Работы приняли по акту, сроки немного сдвинулись.",
        status=Review.Status.APPROVED,
        quality_rating=5,
        timeline_rating=4,
        communication_rating=4,
    )
    Review.objects.create(
        company=company,
        author_name="Черновик",
        title="Pending",
        body="Pending body",
        status=Review.Status.PENDING,
        quality_rating=1,
        timeline_rating=1,
        communication_rating=1,
    )

    assert list(Review.objects.public()) == [approved]
    assert approved.average_rating == 4.3
    assert approved.is_public is True
    assert str(approved) == "Alma Remont · Сделали ремонт"


@pytest.mark.django_db
def test_review_rating_validation_rejects_values_outside_one_to_five():
    company = Company.objects.create(name="Alma Remont", slug="alma-remont")
    review = Review(
        company=company,
        author_name="Клиент",
        title="Bad rating",
        body="Body",
        quality_rating=6,
        timeline_rating=3,
        communication_rating=3,
    )

    with pytest.raises(ValidationError):
        review.full_clean()


@pytest.mark.django_db
def test_rating_snapshot_from_public_reviews():
    company = Company.objects.create(name="Alma Remont", slug="alma-remont")
    Review.objects.create(company=company, author_name="A", title="One", body="Body", status=Review.Status.APPROVED, quality_rating=5, timeline_rating=5, communication_rating=4)
    Review.objects.create(company=company, author_name="B", title="Two", body="Body", status=Review.Status.APPROVED, quality_rating=4, timeline_rating=3, communication_rating=3)
    Review.objects.create(company=company, author_name="C", title="Pending", body="Body", status=Review.Status.PENDING, quality_rating=1, timeline_rating=1, communication_rating=1)

    snapshot = RatingSnapshot.objects.rebuild_for_company(company)

    assert snapshot.company == company
    assert snapshot.review_count == 2
    assert snapshot.average_rating == 4.0
    assert snapshot.quality_rating == 4.5
    assert snapshot.timeline_rating == 4.0
    assert snapshot.communication_rating == 3.5
    assert str(snapshot) == "Alma Remont · 4.0 · 2 reviews"
