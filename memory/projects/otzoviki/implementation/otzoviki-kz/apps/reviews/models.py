from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from apps.companies.models import Company


RATING_VALIDATORS = [MinValueValidator(1), MaxValueValidator(5)]


class PublicReviewQuerySet(models.QuerySet):
    def public(self):
        return self.filter(status=Review.Status.APPROVED).select_related("company").order_by("-published_at", "-created_at")


class Review(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        DISPUTED = "disputed", "Disputed"

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="reviews")
    author_name = models.CharField(max_length=120)
    title = models.CharField(max_length=220)
    body = models.TextField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    quality_rating = models.PositiveSmallIntegerField(validators=RATING_VALIDATORS)
    timeline_rating = models.PositiveSmallIntegerField(validators=RATING_VALIDATORS)
    price_rating = models.PositiveSmallIntegerField(validators=RATING_VALIDATORS, default=3)
    communication_rating = models.PositiveSmallIntegerField(validators=RATING_VALIDATORS)
    warranty_rating = models.PositiveSmallIntegerField(validators=RATING_VALIDATORS, default=3)
    overall_rating = models.PositiveSmallIntegerField(validators=RATING_VALIDATORS, default=3)
    private_proof_note = models.TextField(blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PublicReviewQuerySet.as_manager()

    class Meta:
        ordering = ["-published_at", "-created_at"]

    def save(self, *args, **kwargs):
        if self.status == self.Status.APPROVED and self.published_at is None:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company.name} · {self.title}"

    @property
    def is_public(self) -> bool:
        return self.status == self.Status.APPROVED

    @property
    def average_rating(self) -> float:
        return round((self.quality_rating + self.timeline_rating + self.communication_rating) / 3, 1)


class RatingSnapshotManager(models.Manager):
    def rebuild_for_company(self, company: Company):
        reviews = list(Review.objects.public().filter(company=company))
        count = len(reviews)
        if count:
            quality = round(sum(r.quality_rating for r in reviews) / count, 1)
            timeline = round(sum(r.timeline_rating for r in reviews) / count, 1)
            communication = round(sum(r.communication_rating for r in reviews) / count, 1)
            average = round((quality + timeline + communication) / 3, 1)
        else:
            quality = timeline = communication = average = 0
        snapshot, _ = self.update_or_create(
            company=company,
            defaults={
                "review_count": count,
                "average_rating": average,
                "quality_rating": quality,
                "timeline_rating": timeline,
                "communication_rating": communication,
            },
        )
        return snapshot


class RatingSnapshot(models.Model):
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name="rating_snapshot")
    review_count = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    quality_rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    timeline_rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    communication_rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    objects = RatingSnapshotManager()

    class Meta:
        ordering = ["-average_rating", "company__name"]

    def __str__(self):
        return f"{self.company.name} · {self.average_rating} · {self.review_count} reviews"


class ReviewModerationLog(models.Model):
    class Action(models.TextChoices):
        PUBLISHED = "published", "Published"
        REJECTED = "rejected", "Rejected"
        DISPUTED = "disputed", "Disputed"
        UPDATED = "updated", "Updated"

    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="moderation_logs")
    moderator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="review_moderation_logs")
    action = models.CharField(max_length=24, choices=Action.choices)
    from_status = models.CharField(max_length=16, blank=True)
    to_status = models.CharField(max_length=16, blank=True)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"{self.review.company.name} · {self.review.title} · {self.action}"
