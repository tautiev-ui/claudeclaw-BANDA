import csv
import io
from pathlib import Path

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command

from apps.launchqa.models import WebmasterSetupTask


@pytest.mark.django_db
def test_prepare_launch_operator_readiness_creates_manual_webmaster_tasks_and_docs():
    call_command("prepare_launch_operator_readiness")

    assert WebmasterSetupTask.objects.count() >= 8
    assert WebmasterSetupTask.objects.filter(platform=WebmasterSetupTask.Platform.YANDEX).exists()
    assert WebmasterSetupTask.objects.filter(platform=WebmasterSetupTask.Platform.GOOGLE).exists()
    assert Path("docs/launch-origin-cdn-bot-qa.md").exists()
    body = Path("docs/launch-origin-cdn-bot-qa.md").read_text()
    assert "Cloudflare DNS-only fallback" in body
    assert "YandexBot-like fetch" in body
    assert "No JS Challenge" in body


@pytest.mark.django_db
def test_operator_readiness_csv_exports_are_staff_only_and_manual_safe(client):
    for path in ["/admin/launch-qa/operator-readiness.csv", "/admin/launch-qa/origin-bot-qa.csv"]:
        response = client.get(path)
        assert response.status_code == 302
        assert "/admin/login/" in response["Location"]

    call_command("prepare_launch_operator_readiness")
    staff = get_user_model().objects.create_user(username="operator-readiness", password="pass", is_staff=True)
    client.force_login(staff)

    response = client.get("/admin/launch-qa/operator-readiness.csv")
    assert response.status_code == 200
    assert response["Content-Type"] == "text/csv; charset=utf-8"
    rows = list(csv.DictReader(io.StringIO(response.content.decode())))
    assert rows
    assert {"area", "item", "status", "manual_required", "secret_safe", "notes"}.issubset(rows[0].keys())
    assert all(row["secret_safe"] == "true" for row in rows)
    assert any(row["area"] == "Yandex Webmaster" for row in rows)
    assert any(row["area"] == "Google Search Console" for row in rows)
    assert any(row["manual_required"] == "true" for row in rows)

    response = client.get("/admin/launch-qa/origin-bot-qa.csv")
    assert response.status_code == 200
    assert response["Content-Type"] == "text/csv; charset=utf-8"
    rows = list(csv.DictReader(io.StringIO(response.content.decode())))
    assert rows
    assert {"check_key", "status", "manual_required", "external_network_used", "notes"}.issubset(rows[0].keys())
    assert all(row["external_network_used"] == "false" for row in rows)
    assert any(row["check_key"] == "cloudflare_dns_only_fallback" for row in rows)
    assert any(row["check_key"] == "yandexbot_like_fetch" for row in rows)
