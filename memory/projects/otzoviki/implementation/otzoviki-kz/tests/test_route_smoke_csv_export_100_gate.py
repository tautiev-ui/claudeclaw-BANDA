import csv
import io

import pytest
from django.contrib.auth import get_user_model


EXPECTED_COLUMNS = [
    "gate_number",
    "gate",
    "route_label",
    "path_pattern",
    "expected_status",
    "expected_robots",
    "expected_content_type",
    "auth_requirement",
    "canonical_requirement",
    "schema_requirement",
    "sitemap_requirement",
    "launch_risk_if_fails",
    "manual_probe_note",
]


@pytest.mark.django_db
def test_route_smoke_export_requires_staff(client):
    response = client.get("/admin/launch-qa/route-smoke-export.csv")

    assert response.status_code == 302
    assert "/admin/login/" in response["Location"]


@pytest.mark.django_db
def test_route_smoke_export_returns_100_gate_csv(client):
    staff = get_user_model().objects.create_user(username="route-smoke-csv", password="pass", is_staff=True)
    client.force_login(staff)

    response = client.get("/admin/launch-qa/route-smoke-export.csv")

    assert response.status_code == 200
    assert response["Content-Type"] == "text/csv; charset=utf-8"
    assert response["Content-Disposition"] == 'attachment; filename="route-smoke-matrix.csv"'
    rows = list(csv.DictReader(io.StringIO(response.content.decode())))
    assert len(rows) == 100
    assert list(rows[0].keys()) == EXPECTED_COLUMNS
    assert rows[0]["gate_number"] == "1"
    assert rows[-1]["gate_number"] == "100"
    gates = {row["gate"] for row in rows}
    paths = {row["path_pattern"] for row in rows}
    for marker in [
        "100-gate route smoke CSV export",
        "Staff-only CSV export",
        "Yandex submit only green routes",
        "Google submit only green routes",
        "Noindex routes excluded from sitemap",
        "Private/admin routes excluded from sitemap",
        "Canonical has no query or fragment",
        "Schema only when visible evidence supports it",
        "Paid profile neutrality must be visible",
        "Manual post-deploy probe required",
    ]:
        assert marker in gates, marker
    for path in [
        "/",
        "/kz/",
        "/kz/almaty/",
        "/kz/almaty/remont-kvartir/",
        "/kz/company/{slug}/",
        "/kz/guides/",
        "/claim-profile/",
        "/business/dashboard/",
        "/robots.txt",
        "/sitemap.xml",
        "/llms.txt",
        "/ai-reputation.md",
        "/admin/launch-qa/route-smoke/",
    ]:
        assert path in paths, path
    assert any(row["expected_content_type"] == "text/plain" and row["path_pattern"] == "/robots.txt" for row in rows)
    assert any(row["expected_content_type"] == "application/xml" and row["path_pattern"] == "/sitemap.xml" for row in rows)
    assert any(row["auth_requirement"] == "staff-only" and row["path_pattern"] == "/admin/launch-qa/route-smoke/" for row in rows)
    assert any(row["expected_robots"] == "noindex,follow" and row["path_pattern"] == "/business/dashboard/" for row in rows)


@pytest.mark.django_db
def test_route_smoke_pages_link_csv_export(client):
    staff = get_user_model().objects.create_user(username="route-smoke-csv-link", password="pass", is_staff=True)
    client.force_login(staff)

    for path in ["/admin/launch-qa/", "/admin/launch-qa/route-smoke/"]:
        response = client.get(path)
        assert response.status_code == 200
        assert "/admin/launch-qa/route-smoke-export.csv" in response.content.decode()
