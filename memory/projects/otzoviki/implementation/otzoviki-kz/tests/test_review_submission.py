import pytest

from apps.companies.models import Company
from apps.evidence.models import Evidence
from apps.reviews.models import Review


@pytest.mark.django_db
def test_review_submission_page_links_policy_and_anti_defamation_guidance(client):
    company = Company.objects.create(name="Alma Remont", slug="alma-remont")

    response = client.get(f"/kz/company/{company.slug}/reviews/new/")

    assert response.status_code == 200
    html = response.content.decode()
    assert "Правила отзывов" in html
    assert "/review-policy/" in html
    assert "пишите факты" in html.lower()


@pytest.mark.django_db
def test_review_submission_creates_pending_review_and_never_publishes_immediately(client):
    company = Company.objects.create(name="Alma Remont", slug="alma-remont")

    response = client.post(
        f"/kz/company/{company.slug}/reviews/new/",
        {
            "author_name": "Клиент",
            "title": "Сделали ремонт",
            "body": "Работы приняли по акту, есть договор и гарантия.",
            "quality_rating": "5",
            "timeline_rating": "4",
            "price_rating": "4",
            "communication_rating": "4",
            "warranty_rating": "5",
            "overall_rating": "5",
            "private_proof_note": "Договор и акт есть, могу предоставить модератору.",
        },
    )

    assert response.status_code == 302
    review = Review.objects.get(company=company)
    assert review.status == Review.Status.PENDING
    assert review.published_at is None
    assert review.price_rating == 4
    assert review.warranty_rating == 5
    assert review.overall_rating == 5
    assert Review.objects.public().count() == 0
    private_proof = Evidence.objects.get(company=company, evidence_type=Evidence.EvidenceType.PRIVATE_PROOF)
    assert private_proof.review == review
    assert private_proof.visibility == Evidence.Visibility.PRIVATE
    assert "Договор и акт" in private_proof.claim
    assert Evidence.objects.public().count() == 0


@pytest.mark.django_db
def test_review_submission_rejects_invalid_rating(client):
    company = Company.objects.create(name="Alma Remont", slug="alma-remont")

    response = client.post(
        f"/kz/company/{company.slug}/reviews/new/",
        {
            "author_name": "Клиент",
            "title": "Bad",
            "body": "Body",
            "quality_rating": "6",
            "timeline_rating": "4",
            "price_rating": "4",
            "communication_rating": "4",
            "warranty_rating": "4",
            "overall_rating": "4",
        },
    )

    assert response.status_code == 200
    assert Review.objects.count() == 0
    assert "Исправьте ошибки" in response.content.decode()
