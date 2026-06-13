import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.ai_evidence.forms import AIYandexEvidenceCaptureForm
from apps.ai_evidence.models import AIYandexEvidenceLog
from apps.companies.models import Company


@pytest.mark.django_db
def test_ai_evidence_capture_form_defaults_to_private_visibility():
    form = AIYandexEvidenceCaptureForm()

    assert form.fields["visibility"].initial == AIYandexEvidenceLog.Visibility.PRIVATE


@pytest.mark.django_db
def test_ai_evidence_capture_form_forces_screenshot_submissions_private_even_if_public_requested(settings):
    settings.MEDIA_ROOT = "/tmp/otzoviki-test-media"
    company = Company.objects.create(name="Alma Remont", slug="alma-remont-capture")
    form = AIYandexEvidenceCaptureForm(
        data={
            "company": company.id,
            "platform": AIYandexEvidenceLog.Platform.YANDEX_NEURO,
            "query": "Alma Remont отзывы",
            "region": "Алматы",
            "answer_excerpt": "Sensitive screenshot excerpt.",
            "cited_sources_text": "https://yandex.kz/maps/org/example/",
            "sentiment": AIYandexEvidenceLog.Sentiment.MIXED,
            "visibility": AIYandexEvidenceLog.Visibility.PUBLIC,
        },
        files={"screenshot": SimpleUploadedFile("sensitive.png", b"fake-image", content_type="image/png")},
    )

    assert form.is_valid(), form.errors
    log = form.save()

    assert log.visibility == AIYandexEvidenceLog.Visibility.PRIVATE
    assert not log.is_public_safe
    assert log.cited_sources == ["https://yandex.kz/maps/org/example/"]
