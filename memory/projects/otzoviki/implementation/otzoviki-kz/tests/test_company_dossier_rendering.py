import pytest
from django.core.files.base import ContentFile
from django.utils import timezone

from apps.ai_evidence.models import AIYandexEvidenceLog
from apps.business.models import BusinessAccount, BusinessRepresentative, OfficialResponse
from apps.companies.models import Company, CompanyService
from apps.evidence.models import Evidence
from apps.locations.models import City, Country
from apps.reviews.models import RatingSnapshot, Review
from apps.seo.indexability import IndexabilityStatus
from apps.services.models import Service, ServiceCategory


@pytest.mark.django_db
def test_company_dossier_renders_public_reviews_evidence_response_and_ai_logs(client):
    country = Country.objects.create(code="KZ", name="Казахстан", slug="kz")
    city = City.objects.create(country=country, name="Алматы", slug="almaty")
    category = ServiceCategory.objects.create(name="Ремонт", slug="remont")
    service = Service.objects.create(category=category, name="Ремонт квартир", slug="remont-kvartir")
    company = Company.objects.create(
        name="Alma Remont",
        slug="alma-remont",
        short_description="Ремонт квартир в Алматы",
        profile_status=Company.ProfileStatus.CLAIMED,
        index_status=IndexabilityStatus.INDEXABLE,
        seo_title="Alma Remont отзывы",
        seo_description="Отзывы, досье и официальный ответ Alma Remont",
        source_count=3,
        last_verified_at=timezone.now(),
        methodology_version="mvp-1",
    )
    CompanyService.objects.create(company=company, city=city, service=service, is_primary=True)
    RatingSnapshot.objects.create(company=company, review_count=1, average_rating=4.3, quality_rating=5, timeline_rating=4, communication_rating=4)
    Review.objects.create(company=company, author_name="Клиент", title="Сдали по акту", body="Есть договор и гарантия.", status=Review.Status.APPROVED, quality_rating=5, timeline_rating=4, communication_rating=4)
    Review.objects.create(company=company, author_name="Черновик", title="Не видно", body="Pending", status=Review.Status.PENDING, quality_rating=1, timeline_rating=1, communication_rating=1)
    Evidence.objects.create(company=company, evidence_type=Evidence.EvidenceType.EXTERNAL_FOOTPRINT, title="Карточка Яндекс", claim="Есть карточка в Яндекс Картах", source_url="https://yandex.kz/maps/org/example/", visibility=Evidence.Visibility.PUBLIC, captured_at=timezone.now())
    Evidence.objects.create(company=company, evidence_type=Evidence.EvidenceType.PRIVATE_PROOF, title="Договор клиента", claim="Private", visibility=Evidence.Visibility.PRIVATE, captured_at=timezone.now())
    account = BusinessAccount.objects.create(company=company, display_name="Alma Business")
    representative = BusinessRepresentative.objects.create(account=account, full_name="Айдар", email="owner@example.com")
    OfficialResponse.objects.create(company=company, representative=representative, body="Готовы предоставить акты и гарантию.", status=OfficialResponse.Status.PUBLISHED)
    AIYandexEvidenceLog.objects.create(company=company, platform=AIYandexEvidenceLog.Platform.YANDEX_NEURO, query="Alma Remont отзывы", region="Алматы", answer_excerpt="Упоминается в картах и отзывах.", visibility=AIYandexEvidenceLog.Visibility.PUBLIC)

    response = client.get(company.get_absolute_url())

    assert response.status_code == 200
    html = response.content.decode()
    assert '<meta name="robots" content="index,follow">' in html
    assert '<link rel="canonical" href="http://testserver/kz/company/alma-remont/">' in html
    assert '"@type": "BreadcrumbList"' in html
    assert '"@type": "HomeAndConstructionBusiness"' in html
    assert '"aggregateRating"' in html
    assert "Ремонт квартир в Алматы" in html
    assert "Trust summary" in html
    assert "claimed" in html
    assert "sources: 3" in html
    assert "methodology: mvp-1" in html
    assert "Услуги и города" in html
    assert "/kz/almaty/remont-kvartir/" in html
    assert "Рейтинг Otzoviki" in html
    assert "4.3" in html
    assert "качество: 5.0" in html
    assert "сроки: 4.0" in html
    assert "коммуникация: 4.0" in html
    assert "Как читать это досье" in html
    assert "Отзывы Otzoviki" in html
    assert "Сдали по акту" in html
    assert "External footprint" in html
    assert "Карточка Яндекс" in html
    assert 'href="https://yandex.kz/maps/org/example/" rel="nofollow noopener noreferrer" target="_blank"' in html
    assert "Официальный ответ" in html
    assert "Готовы предоставить акты" in html
    assert "Yandex / AI evidence" in html
    assert "Alma Remont отзывы" in html
    assert "Приватные доказательства не публикуются" in html
    assert "Платный профиль не влияет на рейтинг" in html
    assert "/right-of-reply/" in html
    assert "/review-policy/" in html
    assert "/methodology/" in html
    assert "/reputation-audit/" in html
    assert "/kz/company/alma-remont/official-response/new/" in html
    assert "Репутационный паспорт" in html
    assert "Внешний след по площадкам" in html
    assert "Yandex Maps" in html
    assert "2GIS" in html
    assert "Google Business" in html
    assert "Review intelligence" in html
    assert "Плюсы" in html
    assert "Минусы и риски" in html
    assert "Evidence locker" in html
    assert "Profile completeness" in html
    assert "Claim / audit CTA" in html
    assert "Не видно" not in html
    assert "Договор клиента" not in html


@pytest.mark.django_db
def test_company_dossier_excludes_ai_evidence_with_screenshot_even_if_public(client, settings):
    settings.MEDIA_ROOT = "/tmp/otzoviki-test-media"
    company = Company.objects.create(name="Alma Remont", slug="alma-remont-ai-safe")
    public_safe = AIYandexEvidenceLog.objects.create(
        company=company,
        platform=AIYandexEvidenceLog.Platform.YANDEX_NEURO,
        query="safe public query",
        region="Алматы",
        answer_excerpt="Public-safe excerpt.",
        visibility=AIYandexEvidenceLog.Visibility.PUBLIC,
    )
    sensitive = AIYandexEvidenceLog.objects.create(
        company=company,
        platform=AIYandexEvidenceLog.Platform.AI_OVERVIEW,
        query="sensitive screenshot query",
        region="Алматы",
        answer_excerpt="Sensitive screenshot excerpt.",
        visibility=AIYandexEvidenceLog.Visibility.PUBLIC,
    )
    sensitive.screenshot.save("sensitive.png", ContentFile(b"fake-image"), save=True)

    response = client.get(company.get_absolute_url())
    html = response.content.decode()

    assert response.status_code == 200
    assert public_safe.is_public_safe
    assert not sensitive.is_public_safe
    assert "safe public query" in html
    assert "sensitive screenshot query" not in html
    assert "Sensitive screenshot excerpt" not in html


@pytest.mark.django_db
def test_company_dossier_empty_state_stays_noindex_safe(client):
    company = Company.objects.create(name="Empty Remont", slug="empty-remont")

    response = client.get(company.get_absolute_url())

    assert response.status_code == 200
    html = response.content.decode()
    assert '<meta name="robots" content="noindex,follow">' in html
    assert "Досье ещё заполняется" in html
