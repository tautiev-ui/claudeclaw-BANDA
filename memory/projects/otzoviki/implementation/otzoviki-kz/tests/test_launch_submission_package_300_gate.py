import csv
import io

import pytest
from django.contrib.auth import get_user_model


SUBMISSION_JSON_GATES = ["100-gate launch submission JSON package", "Staff-only submission JSON", "Stable submission JSON schema", "Versioned submission JSON payload", "Generated submission metadata", "Deployment handoff source embedded", "Release readiness source embedded", "Blockers source embedded", "Route smoke source embedded", "Sitemap source embedded", "Robots source embedded", "LLMS source embedded", "AI reputation source embedded", "Yandex manual submission plan JSON", "Google manual submission plan JSON", "IndexNow manual submission plan JSON", "Sitemap manual submission plan JSON", "AI crawler docs manual plan JSON", "No external network JSON", "No credential usage JSON", "No state mutation JSON", "GET-only JSON", "Manual operator required JSON", "Production host placeholder JSON", "Deploy revision placeholder JSON", "Submit actor placeholder JSON", "Submitted at placeholder JSON", "Yandex sitemap step JSON", "Yandex important pages step JSON", "Yandex recrawl docs step JSON", "Yandex monitor step JSON", "Google sitemap step JSON", "Google URL inspection step JSON", "Google monitor step JSON", "IndexNow endpoint placeholder JSON", "IndexNow allowed urls only JSON", "IndexNow no admin urls JSON", "IndexNow no noindex urls JSON", "Sitemap canonical only JSON", "Sitemap no query fragments JSON", "Sitemap robots allowed JSON", "Sitemap no private urls JSON", "AI docs llms allowed JSON", "AI docs reputation allowed JSON", "AI docs methodology allowed JSON", "AI docs no private evidence JSON", "AI docs no business dashboard JSON", "AI docs no admin exposure JSON", "Public submit inventory JSON", "Policy submit inventory JSON", "City/service submit inventory JSON", "Company submit inventory JSON", "Guide submit inventory JSON", "Machine docs submit inventory JSON", "Held noindex inventory JSON", "Admin excluded inventory JSON", "Business excluded inventory JSON", "Search excluded inventory JSON", "QR excluded inventory JSON", "Lead forms excluded inventory JSON", "Review forms excluded inventory JSON", "Official response forms excluded JSON", "Claim forms excluded JSON", "Manual action Yandex login JSON", "Manual action Google login JSON", "Manual action IndexNow key check JSON", "Manual action sitemap fetch JSON", "Manual action robots fetch JSON", "Manual action llms fetch JSON", "Manual action ai reputation fetch JSON", "Success criterion sitemap accepted JSON", "Success criterion robots accessible JSON", "Success criterion docs accessible JSON", "Success criterion no blockers JSON", "Success criterion route smoke green JSON", "Success criterion no 5xx JSON", "Success criterion no private indexable JSON", "Success criterion no unsafe schema JSON", "Rollback trigger submit blockers JSON", "Rollback trigger sitemap malformed JSON", "Rollback trigger robots disallow JSON", "Rollback trigger private exposure JSON", "Rollback trigger docs leakage JSON", "Monitoring first hour JSON", "Monitoring first day JSON", "Yandex crawl watch JSON", "Google crawl watch JSON", "AI crawler fetch watch JSON", "404 watch JSON", "500 watch JSON", "Index coverage watch JSON", "Manual notes field JSON", "Risk level field JSON", "Allowed field JSON", "Source path field JSON", "Submission target field JSON", "Submission tool field JSON", "Linked from launch ops JSON", "Linked from deployment handoff JSON", "Next 300-gate submission evidence queue"]
SUBMISSION_CSV_GATES = [gate.replace("launch submission JSON package", "launch submission CSV package").replace("JSON", "CSV") for gate in SUBMISSION_JSON_GATES]
SUBMISSION_LIVE_GATES = [gate.replace("launch submission JSON package", "launch submission live package").replace("JSON", "LIVE") for gate in SUBMISSION_JSON_GATES]

EXPECTED_CSV_COLUMNS = ["gate_number", "gate", "submission_target", "submission_tool", "status", "allowed", "source_path", "manual_action", "launch_risk_if_fails"]

@pytest.mark.django_db
def test_launch_submission_package_requires_staff(client):
    for path in ["/admin/launch-qa/submission-package.json", "/admin/launch-qa/submission-package.csv", "/admin/launch-qa/submission-package-live.json"]:
        response = client.get(path)
        assert response.status_code == 302
        assert "/admin/login/" in response["Location"]

@pytest.mark.django_db
def test_launch_submission_json_returns_100_gate_contract(client):
    staff = get_user_model().objects.create_user(username="submit-json", password="pass", is_staff=True)
    client.force_login(staff)
    response = client.get("/admin/launch-qa/submission-package.json")
    assert response.status_code == 200
    assert response["Content-Type"] == "application/json"
    payload = response.json()
    assert payload["schema"] == "otzoviki.launch_submission_package.v1"
    assert payload["version"] == "100-gate-launch-submission-json"
    assert payload["count"] == 100
    assert payload["staff_only"] is True
    assert payload["robots"] == "noindex,follow"
    assert payload["generated_by"] == "launchqa.submission_package_json"
    assert payload["release_phase"] == "post-deploy-manual-submission"
    assert payload["external_network_used"] is False
    assert payload["production_credentials_required"] is False
    assert payload["mutates_state"] is False
    assert payload["method"] == "GET"
    assert payload["operator_required"] is True
    assert payload["go_no_go"]["status"] == "go"
    assert payload["summary"]["failed"] == 0
    assert payload["sources"]["deployment_handoff"] == "/admin/launch-qa/deployment-handoff/"
    assert payload["sources"]["sitemap"] == "/sitemap.xml"
    assert payload["sources"]["robots"] == "/robots.txt"
    assert payload["sources"]["llms"] == "/llms.txt"
    assert payload["sources"]["ai_reputation"] == "/ai-reputation.md"
    assert payload["links"]["csv"] == "/admin/launch-qa/submission-package.csv"
    assert payload["links"]["live"] == "/admin/launch-qa/submission-package-live.json"
    assert len(payload["gates"]) == 100
    assert payload["gates"][0] == "100-gate launch submission JSON package"
    assert payload["gates"][-1] == "Next 300-gate submission evidence queue"
    for gate in SUBMISSION_JSON_GATES:
        assert gate in payload["gates"], gate
    for key in ["yandex", "google", "indexnow", "sitemap", "ai_docs", "excluded"]:
        assert key in payload["submission_plan"]
        assert payload["submission_plan"][key]

@pytest.mark.django_db
def test_launch_submission_csv_returns_100_gate_contract(client):
    staff = get_user_model().objects.create_user(username="submit-csv", password="pass", is_staff=True)
    client.force_login(staff)
    response = client.get("/admin/launch-qa/submission-package.csv")
    assert response.status_code == 200
    assert response["Content-Type"] == "text/csv; charset=utf-8"
    assert response["Content-Disposition"] == 'attachment; filename="launch-submission-package.csv"'
    rows = list(csv.DictReader(io.StringIO(response.content.decode())))
    assert len(rows) == 100
    assert list(rows[0].keys()) == EXPECTED_CSV_COLUMNS
    assert rows[0]["gate_number"] == "1"
    assert rows[-1]["gate_number"] == "100"
    gates = {row["gate"] for row in rows}
    for gate in SUBMISSION_CSV_GATES:
        assert gate in gates, gate
    assert any(row["submission_target"] == "Yandex Webmaster" for row in rows)
    assert any(row["submission_target"] == "Google Search Console" for row in rows)
    assert any(row["source_path"] == "/sitemap.xml" for row in rows)
    assert any(row["allowed"] == "false" for row in rows)

@pytest.mark.django_db
def test_launch_submission_live_returns_100_gate_contract(client):
    staff = get_user_model().objects.create_user(username="submit-live", password="pass", is_staff=True)
    client.force_login(staff)
    response = client.get("/admin/launch-qa/submission-package-live.json")
    assert response.status_code == 200
    assert response["Content-Type"] == "application/json"
    payload = response.json()
    assert payload["schema"] == "otzoviki.launch_submission_package_live.v1"
    assert payload["version"] == "100-gate-launch-submission-live"
    assert payload["count"] == 100
    assert payload["staff_only"] is True
    assert payload["robots"] == "noindex,follow"
    assert payload["generated_by"] == "launchqa.submission_package_live"
    assert payload["summary"]["failed"] == 0
    assert payload["go_no_go"]["status"] == "go"
    assert len(payload["gates"]) == 100
    assert payload["gates"][0] == "100-gate launch submission live package"
    assert payload["gates"][-1] == "Next 300-gate submission evidence queue"
    for gate in SUBMISSION_LIVE_GATES:
        assert gate in payload["gates"], gate
    for key in ["deployment_handoff", "sitemap", "robots", "llms", "ai_reputation", "submission_json", "submission_csv"]:
        assert payload["live_checks"][key]["passed"] is True

@pytest.mark.django_db
def test_launch_submission_package_links_are_visible_from_launch_surfaces(client):
    staff = get_user_model().objects.create_user(username="submit-links", password="pass", is_staff=True)
    client.force_login(staff)
    expected_links = ["/admin/launch-qa/submission-package.json", "/admin/launch-qa/submission-package.csv", "/admin/launch-qa/submission-package-live.json"]
    for path in ["/admin/launch-qa/", "/admin/launch-qa/blockers/", "/admin/launch-qa/deployment-handoff/"]:
        response = client.get(path)
        assert response.status_code == 200
        html = response.content.decode()
        for link in expected_links:
            assert link in html, f"{link} missing from {path}"
