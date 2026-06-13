import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import RequestFactory

from apps.companies.models import Company
from apps.evidence.models import Evidence
from apps.reviews.admin import ReviewAdmin, ReviewPrivateProofEvidenceInline
from apps.reviews.models import RatingSnapshot, Review, ReviewModerationLog


def create_review(status=Review.Status.PENDING, slug="alma-remont"):
    company = Company.objects.create(name=f"Alma Remont {slug}", slug=slug)
    return Review.objects.create(
        company=company,
        author_name="Клиент",
        title="Сделали ремонт",
        body="Фактический отзыв",
        status=status,
        quality_rating=5,
        timeline_rating=4,
        price_rating=4,
        communication_rating=4,
        warranty_rating=5,
        overall_rating=5,
    )


@pytest.mark.django_db
def test_review_supports_disputed_moderation_status():
    review = create_review(status=Review.Status.DISPUTED)

    assert review.status == "disputed"
    assert Review.objects.public().count() == 0


@pytest.mark.django_db
def test_review_admin_moderation_actions_log_publish_reject_and_dispute():
    user = get_user_model().objects.create_superuser(username="moderator", password="pass", email="m@example.com")
    request = RequestFactory().post("/admin/reviews/review/")
    request.user = user
    model_admin = ReviewAdmin(Review, AdminSite())

    publish_review = create_review(slug="publish-remont")
    reject_review = create_review(slug="reject-remont")
    dispute_review = create_review(slug="dispute-remont")

    model_admin.mark_published(request, Review.objects.filter(id=publish_review.id))
    model_admin.mark_rejected(request, Review.objects.filter(id=reject_review.id))
    model_admin.mark_disputed(request, Review.objects.filter(id=dispute_review.id))

    publish_review.refresh_from_db()
    reject_review.refresh_from_db()
    dispute_review.refresh_from_db()
    assert publish_review.status == Review.Status.APPROVED
    assert publish_review.published_at is not None
    assert reject_review.status == Review.Status.REJECTED
    assert dispute_review.status == Review.Status.DISPUTED
    assert ReviewModerationLog.objects.filter(review=publish_review, action=ReviewModerationLog.Action.PUBLISHED, moderator=user).exists()
    assert ReviewModerationLog.objects.filter(review=reject_review, action=ReviewModerationLog.Action.REJECTED, moderator=user).exists()
    assert ReviewModerationLog.objects.filter(review=dispute_review, action=ReviewModerationLog.Action.DISPUTED, moderator=user).exists()


@pytest.mark.django_db
def test_review_admin_moderation_rebuilds_rating_snapshot_for_changed_company():
    user = get_user_model().objects.create_superuser(username="moderator3", password="pass", email="m3@example.com")
    request = RequestFactory().post("/admin/reviews/review/")
    request.user = user
    model_admin = ReviewAdmin(Review, AdminSite())
    company = Company.objects.create(name="Alma Remont", slug="alma-remont-ratings")
    review = Review.objects.create(
        company=company,
        author_name="Клиент",
        title="Сделали ремонт",
        body="Фактический отзыв",
        status=Review.Status.PENDING,
        quality_rating=5,
        timeline_rating=4,
        price_rating=4,
        communication_rating=3,
        warranty_rating=5,
        overall_rating=4,
    )

    model_admin.mark_published(request, Review.objects.filter(id=review.id))

    snapshot = RatingSnapshot.objects.get(company=company)
    assert snapshot.review_count == 1
    assert snapshot.average_rating == 4.0
    review.refresh_from_db()
    model_admin.mark_rejected(request, Review.objects.filter(id=review.id))
    snapshot.refresh_from_db()
    assert snapshot.review_count == 0
    assert snapshot.average_rating == 0


@pytest.mark.django_db
def test_review_moderation_log_is_append_only_and_readable():
    user = get_user_model().objects.create_user(username="editor")
    review = create_review()
    log = ReviewModerationLog.objects.create(review=review, moderator=user, action=ReviewModerationLog.Action.DISPUTED, from_status=Review.Status.PENDING, to_status=Review.Status.DISPUTED, note="Need proof")

    assert str(log) == "Alma Remont alma-remont · Сделали ремонт · disputed"
    assert log.created_at is not None


@pytest.mark.django_db
def test_review_admin_shows_private_proof_evidence_readonly_inline():
    request = RequestFactory().get("/admin/reviews/review/1/change/")
    request.user = get_user_model().objects.create_superuser(username="moderator2", password="pass", email="m2@example.com")
    review_admin = ReviewAdmin(Review, AdminSite())
    inline = ReviewPrivateProofEvidenceInline(Review, AdminSite())
    review = create_review()
    Evidence.objects.create(
        company=review.company,
        review=review,
        evidence_type=Evidence.EvidenceType.PRIVATE_PROOF,
        title="Private proof",
        claim="Договор и акт",
        visibility=Evidence.Visibility.PRIVATE,
        captured_at=review.created_at,
    )

    assert ReviewPrivateProofEvidenceInline in review_admin.inlines
    assert inline.extra == 0
    assert inline.can_delete is False
    assert inline.readonly_fields == ("evidence_type", "title", "claim", "visibility", "captured_at", "created_at")
    assert inline.has_add_permission(request, obj=review) is False
