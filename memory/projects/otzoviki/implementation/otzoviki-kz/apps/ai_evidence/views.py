from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect, render

from .forms import AIYandexEvidenceCaptureForm
from .models import AIYandexEvidenceLog

SEED_QUERY_TEMPLATES = [
    "{brand} отзывы",
    "{brand} жалобы",
    "{brand} рейтинг",
    "{brand} надежная ли",
    "{brand} яндекс отзывы",
    "{brand} 2гис отзывы",
]


@staff_member_required
def ai_evidence_capture(request):
    if request.method == "POST":
        form = AIYandexEvidenceCaptureForm(request.POST, request.FILES)
        if form.is_valid():
            log = form.save()
            return redirect("admin:ai_evidence_aiyandexevidencelog_change", log.pk)
    else:
        form = AIYandexEvidenceCaptureForm(initial={"visibility": AIYandexEvidenceLog.Visibility.PRIVATE})
    return render(
        request,
        "ai_evidence/capture.html",
        {
            "form": form,
            "seed_query_templates": SEED_QUERY_TEMPLATES,
            "page_title": "AI/Yandex evidence capture",
            "robots_meta": "noindex,follow",
        },
    )
