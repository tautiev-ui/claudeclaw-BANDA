import pytest
from django.contrib.auth import get_user_model


@pytest.mark.django_db
def test_route_smoke_live_runner_requires_staff(client):
    response = client.get("/admin/launch-qa/route-smoke-live.json")

    assert response.status_code == 302
    assert "/admin/login/" in response["Location"]


@pytest.mark.django_db
def test_route_smoke_live_runner_returns_100_gate_live_contract(client):
    staff = get_user_model().objects.create_user(username="route-smoke-live", password="pass", is_staff=True)
    client.force_login(staff)

    response = client.get("/admin/launch-qa/route-smoke-live.json")

    assert response.status_code == 200
    assert response["Content-Type"] == "application/json"
    payload = response.json()
    assert payload["schema"] == "otzoviki.route_smoke_live.v1"
    assert payload["version"] == "100-gate-live-runner"
    assert payload["staff_only"] is True
    assert payload["robots"] == "noindex,follow"
    assert payload["source_json"] == "/admin/launch-qa/route-smoke.json"
    assert payload["source_csv"] == "/admin/launch-qa/route-smoke-export.csv"
    assert payload["source_html"] == "/admin/launch-qa/route-smoke/"
    assert payload["count"] == 100
    assert payload["probe_count"] >= 12
    assert payload["passed"] + payload["failed"] == payload["probe_count"]
    assert isinstance(payload["results"], list)
    assert isinstance(payload["gates"], list)
    assert len(payload["gates"]) == 100
    assert len(payload["results"]) == payload["probe_count"]
    assert payload["gates"][0] == "100-gate route smoke live runner"
    assert payload["gates"][-1] == "Next route smoke CI scheduling queue"
    gate_set = set(payload["gates"])
    for marker in [
        "100-gate route smoke live runner",
        "Staff-only live runner",
        "Uses Django test client",
        "Does not call external network",
        "Public routes return expected status",
        "Machine-readable routes return expected content-type",
        "Private/admin routes require auth",
        "Noindex markers checked where expected",
        "Index markers checked where expected",
        "Launch blocker summary emitted",
        "Next route smoke CI scheduling queue",
    ]:
        assert marker in gate_set, marker
    by_path = {result["path"]: result for result in payload["results"]}
    for path in [
        "/",
        "/kz/",
        "/for-business/",
        "/claim-profile/",
        "/reputation-audit/",
        "/business/dashboard/",
        "/robots.txt",
        "/sitemap.xml",
        "/llms.txt",
        "/ai-reputation.md",
        "/admin/launch-qa/",
        "/admin/launch-qa/route-smoke/",
        "/admin/launch-qa/route-smoke.json",
        "/admin/launch-qa/route-smoke-export.csv",
    ]:
        assert path in by_path, path
    assert by_path["/robots.txt"]["content_type"].startswith("text/plain")
    assert by_path["/sitemap.xml"]["content_type"].startswith("application/xml")
    assert by_path["/llms.txt"]["content_type"].startswith("text/plain")
    assert by_path["/ai-reputation.md"]["content_type"].startswith("text/markdown")
    assert by_path["/business/dashboard/"]["expected_status"] == 302
    assert by_path["/business/dashboard/"]["status_code"] == 302
    assert by_path["/admin/launch-qa/"]["status_code"] == 200
    assert by_path["/admin/launch-qa/route-smoke/"]["status_code"] == 200
    assert all("passed" in result and "launch_blocker" in result for result in payload["results"])


@pytest.mark.django_db
def test_route_smoke_pages_link_live_runner(client):
    staff = get_user_model().objects.create_user(username="route-smoke-live-link", password="pass", is_staff=True)
    client.force_login(staff)

    for path in ["/admin/launch-qa/", "/admin/launch-qa/route-smoke/"]:
        response = client.get(path)
        assert response.status_code == 200
        assert "/admin/launch-qa/route-smoke-live.json" in response.content.decode()
