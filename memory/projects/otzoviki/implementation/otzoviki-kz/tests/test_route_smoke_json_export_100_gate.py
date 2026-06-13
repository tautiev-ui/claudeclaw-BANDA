import pytest
from django.contrib.auth import get_user_model


@pytest.mark.django_db
def test_route_smoke_json_export_requires_staff(client):
    response = client.get("/admin/launch-qa/route-smoke.json")

    assert response.status_code == 302
    assert "/admin/login/" in response["Location"]


@pytest.mark.django_db
def test_route_smoke_json_export_returns_100_gate_machine_contract(client):
    staff = get_user_model().objects.create_user(username="route-smoke-json", password="pass", is_staff=True)
    client.force_login(staff)

    response = client.get("/admin/launch-qa/route-smoke.json")

    assert response.status_code == 200
    assert response["Content-Type"] == "application/json"
    payload = response.json()
    assert payload["schema"] == "otzoviki.route_smoke.v1"
    assert payload["version"] == "100-gate-json-export"
    assert payload["count"] == 100
    assert payload["generated_by"] == "launchqa.route_smoke_json"
    assert payload["staff_only"] is True
    assert payload["robots"] == "noindex,follow"
    assert payload["source_csv"] == "/admin/launch-qa/route-smoke-export.csv"
    assert payload["source_html"] == "/admin/launch-qa/route-smoke/"
    assert payload["ops_hub"] == "/admin/launch-qa/"
    assert isinstance(payload["items"], list)
    assert len(payload["items"]) == 100
    first = payload["items"][0]
    last = payload["items"][-1]
    expected_keys = {
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
        "ci_probe_command",
        "yandex_submit_eligible",
        "google_submit_eligible",
        "sitemap_eligible",
        "requires_staff_session",
        "machine_readable",
        "launch_blocker_on_failure",
    }
    assert set(first) == expected_keys
    assert first["gate_number"] == 1
    assert first["gate"] == "100-gate route smoke JSON export"
    assert last["gate_number"] == 100
    assert last["gate"] == "Next route-smoke automation queue"
    gates = {item["gate"] for item in payload["items"]}
    paths = {item["path_pattern"] for item in payload["items"]}
    for marker in [
        "100-gate route smoke JSON export",
        "Staff-only JSON export",
        "Stable schema name",
        "Versioned payload",
        "Generated metadata",
        "CI probe command per row",
        "Yandex eligibility boolean",
        "Google eligibility boolean",
        "Sitemap eligibility boolean",
        "Launch blocker boolean",
        "Next route-smoke automation queue",
    ]:
        assert marker in gates, marker
    for path in [
        "/",
        "/kz/",
        "/kz/company/{slug}/",
        "/business/dashboard/",
        "/robots.txt",
        "/sitemap.xml",
        "/llms.txt",
        "/ai-reputation.md",
        "/admin/launch-qa/route-smoke/",
        "/admin/launch-qa/route-smoke-export.csv",
    ]:
        assert path in paths, path
    assert any(item["path_pattern"] == "/" and item["sitemap_eligible"] is True for item in payload["items"])
    assert any(item["path_pattern"] == "/business/dashboard/" and item["sitemap_eligible"] is False and item["requires_staff_session"] is False for item in payload["items"])
    assert any(item["path_pattern"] == "/admin/launch-qa/route-smoke/" and item["requires_staff_session"] is True for item in payload["items"])
    assert any(item["path_pattern"] == "/robots.txt" and item["machine_readable"] is True for item in payload["items"])


@pytest.mark.django_db
def test_route_smoke_pages_link_json_export(client):
    staff = get_user_model().objects.create_user(username="route-smoke-json-link", password="pass", is_staff=True)
    client.force_login(staff)

    for path in ["/admin/launch-qa/", "/admin/launch-qa/route-smoke/"]:
        response = client.get(path)
        assert response.status_code == 200
        assert "/admin/launch-qa/route-smoke.json" in response.content.decode()
