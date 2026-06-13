import pytest
from django.contrib.auth import get_user_model


BLOCKER_JSON_100_GATES = [
    "100-gate launch blocker JSON export",
    "Staff-only blocker JSON",
    "Stable blocker schema name",
    "Versioned blocker payload",
    "Generated blocker metadata",
    "No external network blocker export",
    "GET-only blocker export",
    "No mutation blocker export",
    "No production credentials blocker export",
    "Live runner summary embedded",
    "Probe count field",
    "Passed count field",
    "Failed count field",
    "Failed paths field",
    "Launch blocker count field",
    "Green launch status field",
    "Red launch status field",
    "Yandex submit allowed boolean",
    "Google submit allowed boolean",
    "Sitemap submit allowed boolean",
    "IndexNow allowed boolean",
    "AI docs allowed boolean",
    "Public release allowed boolean",
    "Admin release allowed boolean",
    "Business workspace allowed boolean",
    "Manual release required boolean",
    "Post deploy smoke required boolean",
    "Source live runner link",
    "Source route smoke JSON link",
    "Source route smoke CSV link",
    "Source route smoke HTML link",
    "Source blocker HTML link",
    "Ops hub link",
    "Home result included",
    "KZ root result included",
    "For-business result included",
    "Claim-profile result included",
    "Reputation-audit result included",
    "Business dashboard redirect included",
    "Robots result included",
    "Sitemap result included",
    "LLMS result included",
    "AI reputation result included",
    "Launch ops result included",
    "Route smoke HTML result included",
    "Route smoke JSON result included",
    "Route smoke CSV result included",
    "Result status code preserved",
    "Result expected status preserved",
    "Result content type preserved",
    "Result expected content type preserved",
    "Result robots marker preserved",
    "Result passed boolean preserved",
    "Result launch blocker boolean preserved",
    "Result response bytes preserved",
    "Result redirect location preserved",
    "Result snippet preserved",
    "Blocker severity critical",
    "Blocker severity warning",
    "Blocker severity manual",
    "Action hold Yandex submit",
    "Action hold Google submit",
    "Action hold sitemap submit",
    "Action hold IndexNow ping",
    "Action verify robots",
    "Action verify sitemap",
    "Action verify AI docs",
    "Action verify private noindex",
    "Action verify lead forms noindex",
    "Action verify business redirect",
    "Action verify admin staff-only",
    "Action verify canonical",
    "Action verify schema",
    "Action verify evidence privacy",
    "Action verify paid neutrality",
    "Action verify right-of-reply",
    "Action verify B2B identity",
    "Action verify moderation queues",
    "Action verify freshness",
    "Action verify indexing monitor",
    "Action verify webmaster checklist",
    "Action verify keyword map",
    "Action verify AI evidence capture",
    "Action verify route smoke CSV",
    "Action verify route smoke JSON",
    "Action verify route smoke live",
    "Action verify blocker HTML",
    "CI-friendly blocker payload",
    "Cron-friendly blocker payload",
    "Post-deploy automation payload",
    "Machine-readable launch decision",
    "Manual owner next action",
    "Safe to cache privately",
    "Do not expose publicly",
    "No sitemap inclusion for blocker JSON",
    "No robots allow requirement for blocker JSON",
    "Blocker export linked from ops hub",
    "Blocker export linked from blocker dashboard",
    "Blocker export linked from route smoke matrix",
    "Next 100-gate release readiness queue",
]


@pytest.mark.django_db
def test_launch_blocker_json_requires_staff(client):
    response = client.get("/admin/launch-qa/blockers.json")

    assert response.status_code == 302
    assert "/admin/login/" in response["Location"]


@pytest.mark.django_db
def test_launch_blocker_json_returns_100_gate_machine_contract(client):
    staff = get_user_model().objects.create_user(username="blocker-json", password="pass", is_staff=True)
    client.force_login(staff)

    response = client.get("/admin/launch-qa/blockers.json")

    assert response.status_code == 200
    assert response["Content-Type"] == "application/json"
    payload = response.json()
    assert payload["schema"] == "otzoviki.launch_blockers.v1"
    assert payload["version"] == "100-gate-blocker-json"
    assert payload["staff_only"] is True
    assert payload["robots"] == "noindex,follow"
    assert payload["count"] == 100
    assert payload["generated_by"] == "launchqa.launch_blocker_json"
    assert payload["source_live_runner"] == "/admin/launch-qa/route-smoke-live.json"
    assert payload["source_route_smoke_json"] == "/admin/launch-qa/route-smoke.json"
    assert payload["source_route_smoke_csv"] == "/admin/launch-qa/route-smoke-export.csv"
    assert payload["source_route_smoke_html"] == "/admin/launch-qa/route-smoke/"
    assert payload["source_blocker_html"] == "/admin/launch-qa/blockers/"
    assert payload["ops_hub"] == "/admin/launch-qa/"
    assert payload["summary"]["probe_count"] >= 10
    assert payload["summary"]["failed"] == 0
    assert payload["summary"]["launch_blocker_count"] == 0
    assert payload["decision"]["launch_status"] == "green"
    assert payload["decision"]["yandex_submit_allowed"] is True
    assert payload["decision"]["google_submit_allowed"] is True
    assert payload["decision"]["sitemap_submit_allowed"] is True
    assert payload["decision"]["indexnow_allowed"] is True
    assert payload["decision"]["manual_release_required"] is True
    assert payload["decision"]["post_deploy_smoke_required"] is True
    assert len(payload["gates"]) == 100
    assert payload["gates"][0] == "100-gate launch blocker JSON export"
    assert payload["gates"][-1] == "Next 100-gate release readiness queue"
    for marker in BLOCKER_JSON_100_GATES:
        assert marker in payload["gates"], marker
    paths = {result["path"] for result in payload["results"]}
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
        assert path in paths, path
    first = payload["results"][0]
    for key in [
        "path",
        "client",
        "expected_status",
        "status_code",
        "expected_content_type",
        "content_type",
        "robots_marker",
        "passed",
        "launch_blocker",
        "response_bytes",
        "snippet",
    ]:
        assert key in first


@pytest.mark.django_db
def test_launch_blocker_json_is_linked_from_ops_blockers_and_route_smoke(client):
    staff = get_user_model().objects.create_user(username="blocker-json-link", password="pass", is_staff=True)
    client.force_login(staff)

    for path in ["/admin/launch-qa/", "/admin/launch-qa/blockers/", "/admin/launch-qa/route-smoke/"]:
        response = client.get(path)
        assert response.status_code == 200
        assert "/admin/launch-qa/blockers.json" in response.content.decode()
