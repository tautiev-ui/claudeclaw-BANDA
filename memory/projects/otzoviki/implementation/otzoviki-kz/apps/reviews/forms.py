from django import forms
from django.utils import timezone

from apps.evidence.models import Evidence
from apps.reviews.models import Review


class ReviewSubmissionForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = [
            "author_name",
            "title",
            "body",
            "quality_rating",
            "timeline_rating",
            "price_rating",
            "communication_rating",
            "warranty_rating",
            "overall_rating",
            "private_proof_note",
        ]
        widgets = {
            "body": forms.Textarea(attrs={"rows": 5}),
            "private_proof_note": forms.Textarea(attrs={"rows": 3}),
        }

    def save(self, commit=True):
        review = super().save(commit=False)
        review.status = Review.Status.PENDING
        review.published_at = None
        if commit:
            review.save()
            self.save_private_evidence(review)
        return review

    def save_private_evidence(self, review: Review):
        proof_note = (self.cleaned_data.get("private_proof_note") or "").strip()
        if not proof_note or not review.company_id:
            return None
        return Evidence.objects.create(
            company=review.company,
            review=review,
            evidence_type=Evidence.EvidenceType.PRIVATE_PROOF,
            title=f"Private proof for review: {review.title}",
            claim=proof_note,
            visibility=Evidence.Visibility.PRIVATE,
            captured_at=timezone.now(),
        )
