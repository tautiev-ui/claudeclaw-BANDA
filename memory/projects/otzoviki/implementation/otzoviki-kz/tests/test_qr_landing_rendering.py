import pytest

from apps.companies.models import Company
from apps.qr.models import QRReviewFlow, QRScanEvent, ReviewPlatformLink


@pytest.mark.django_db
def test_qr_landing_renders_neutral_platform_links_and_noindex(client):
    company = Company.objects.create(name="Alma Remont", slug="alma-remont")
    flow = QRReviewFlow.objects.create(company=company, label="После сдачи объекта")
    ReviewPlatformLink.objects.create(flow=flow, platform=ReviewPlatformLink.Platform.OTZOVIKI, capability=ReviewPlatformLink.Capability.DIRECT_FORM, url="https://otzoviki.kz/kz/company/alma-remont/reviews/new/")
    ReviewPlatformLink.objects.create(flow=flow, platform=ReviewPlatformLink.Platform.YANDEX, capability=ReviewPlatformLink.Capability.PROFILE, url="https://yandex.kz/maps/org/example/")

    response = client.get(flow.get_absolute_url())

    assert response.status_code == 200
    html = response.content.decode()
    assert '<meta name="robots" content="noindex,follow">' in html
    assert "После сдачи объекта" in html
    assert "Otzoviki" in html
    assert "Yandex" in html
    assert f"/r/{flow.token}/yandex/" in html
    assert "https://yandex.kz/maps/org/example/" not in html
    assert "не фильтрует пользователей по настроению" in html.lower()
    assert "выберите любую площадку" in html.lower()


@pytest.mark.django_db
def test_qr_landing_records_scan_without_personal_data(client):
    company = Company.objects.create(name="Alma Remont", slug="alma-remont")
    flow = QRReviewFlow.objects.create(company=company, label="QR")

    client.get(flow.get_absolute_url(), HTTP_USER_AGENT="Mobile Safari")

    flow.refresh_from_db()
    assert flow.scan_count == 1
    event = QRScanEvent.objects.get(flow=flow)
    assert event.user_agent_family == "Mobile Safari"
    assert event.visitor_ip_hash is None


@pytest.mark.django_db
def test_qr_review_flow_never_enables_sentiment_filtering():
    company = Company.objects.create(name="Alma Remont", slug="alma-remont-neutral")

    flow = QRReviewFlow.objects.create(company=company, label="QR", sentiment_filter_enabled=True)
    flow.refresh_from_db()

    assert flow.sentiment_filter_enabled is False


@pytest.mark.django_db
def test_qr_platform_click_redirect_counts_only_active_usable_links(client):
    company = Company.objects.create(name="Alma Remont", slug="alma-remont-click")
    flow = QRReviewFlow.objects.create(company=company, label="QR")
    link = ReviewPlatformLink.objects.create(
        flow=flow,
        platform=ReviewPlatformLink.Platform.YANDEX,
        capability=ReviewPlatformLink.Capability.PROFILE,
        url="https://yandex.kz/maps/org/example/",
    )
    inactive = ReviewPlatformLink.objects.create(
        flow=flow,
        platform=ReviewPlatformLink.Platform.GOOGLE,
        capability=ReviewPlatformLink.Capability.PROFILE,
        url="https://google.com/maps/example",
        is_active=False,
    )

    response = client.get(f"/r/{flow.token}/yandex/")
    inactive_response = client.get(f"/r/{flow.token}/google/")

    link.refresh_from_db()
    inactive.refresh_from_db()
    assert response.status_code == 302
    assert response["Location"] == "https://yandex.kz/maps/org/example/"
    assert link.click_count == 1
    assert inactive_response.status_code == 404
    assert inactive.click_count == 0
