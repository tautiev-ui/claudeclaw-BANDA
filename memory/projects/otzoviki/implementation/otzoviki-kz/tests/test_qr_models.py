import pytest

from apps.companies.models import Company
from apps.qr.models import QRReviewFlow, QRScanEvent, ReviewPlatformLink


@pytest.mark.django_db
def test_qr_review_flow_has_noindex_landing_and_generates_token():
    company = Company.objects.create(name="Alma Remont", slug="alma-remont")
    flow = QRReviewFlow.objects.create(company=company, label="После сдачи объекта")

    assert flow.token
    assert flow.get_absolute_url() == f"/r/{flow.token}/"
    assert flow.robots_meta == "noindex,follow"
    assert flow.is_active is True
    assert str(flow) == "Alma Remont · После сдачи объекта"


@pytest.mark.django_db
def test_review_platform_link_tracks_capability_and_clicks_without_sentiment_gating():
    company = Company.objects.create(name="Alma Remont", slug="alma-remont")
    flow = QRReviewFlow.objects.create(company=company, label="QR стойка")
    link = ReviewPlatformLink.objects.create(
        flow=flow,
        platform=ReviewPlatformLink.Platform.YANDEX,
        capability=ReviewPlatformLink.Capability.PROFILE,
        url="https://yandex.kz/maps/org/example/",
        last_checked_at="2026-06-11T12:00:00Z",
    )

    link.register_click()
    link.refresh_from_db()

    assert link.click_count == 1
    assert link.platform_label == "Yandex"
    assert link.is_usable is True
    assert flow.sentiment_filter_enabled is False


@pytest.mark.django_db
def test_qr_scan_events_are_aggregate_privacy_safe():
    company = Company.objects.create(name="Alma Remont", slug="alma-remont")
    flow = QRReviewFlow.objects.create(company=company, label="QR")

    QRScanEvent.objects.record_scan(flow=flow, user_agent_family="Mobile Safari")
    QRScanEvent.objects.record_scan(flow=flow, user_agent_family="Chrome")

    flow.refresh_from_db()

    assert flow.scan_count == 2
    assert QRScanEvent.objects.filter(flow=flow).count() == 2
    assert QRScanEvent.objects.filter(visitor_ip_hash__isnull=False).count() == 0
