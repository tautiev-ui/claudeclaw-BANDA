from django.shortcuts import get_object_or_404, redirect, render

from apps.analytics.models import AnalyticsEvent, track_event
from apps.companies.models import Company
from apps.reviews.forms import ReviewSubmissionForm


def submit_review(request, slug: str):
    company = get_object_or_404(Company, slug=slug)
    if request.method == "POST":
        form = ReviewSubmissionForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.company = company
            review.save()
            form.save_private_evidence(review)
            track_event(event_type=AnalyticsEvent.EventType.REVIEW_SUBMIT_COMPLETE, request=request, company=company)
            return redirect(company.get_absolute_url())
    else:
        track_event(event_type=AnalyticsEvent.EventType.REVIEW_SUBMIT_START, request=request, company=company)
        form = ReviewSubmissionForm()
    return render(
        request,
        "reviews/submit_review.html",
        {
            "company": company,
            "form": form,
            "page_title": f"Оставить отзыв — {company.name}",
            "page_description": "Форма отзыва с модерацией, правилами публикации и приватным proof note.",
            "robots_meta": "noindex,follow",
            "canonical_url": request.build_absolute_uri(request.path),
            "has_errors": form.is_bound and form.errors,
        },
    )
