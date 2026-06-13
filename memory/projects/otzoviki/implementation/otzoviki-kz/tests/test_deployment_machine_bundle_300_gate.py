import csv
import io

import pytest
from django.contrib.auth import get_user_model


DEPLOYMENT_JSON_GATES = [
    "100-gate deployment handoff JSON export",
    "Staff-only deployment JSON",
    "Stable deployment JSON schema",
    "Versioned deployment JSON payload",
    "Generated deployment metadata",
    "Release readiness embedded",
    "Go/no-go embedded",
    "Manual actions embedded",
    "Source links embedded",
    "Inventory embedded",
    "Pre-deploy checklist JSON",
    "Deploy checklist JSON",
    "Post-deploy checklist JSON",
    "Search submission checklist JSON",
    "Rollback checklist JSON",
    "Monitoring checklist JSON",
    "Yandex submit gate JSON",
    "Google submit gate JSON",
    "IndexNow gate JSON",
    "Sitemap submit gate JSON",
    "AI docs gate JSON",
    "Public release gate JSON",
    "Admin release gate JSON",
    "Business workspace gate JSON",
    "Manual release required JSON",
    "Post-deploy smoke required JSON",
    "Production credentials false JSON",
    "External network false JSON",
    "Mutates state false JSON",
    "GET method JSON",
    "Health probe action JSON",
    "Route smoke live action JSON",
    "Release readiness verify action JSON",
    "Yandex Webmaster action JSON",
    "Google Search Console action JSON",
    "IndexNow action JSON",
    "Rollback if blockers JSON",
    "Rollback if 5xx JSON",
    "Rollback if sitemap malformed JSON",
    "Rollback if robots blocks docs JSON",
    "Rollback if private noindex missing JSON",
    "Rollback if schema unsafe JSON",
    "Rollback if paid neutrality missing JSON",
    "Rollback if review forms indexable JSON",
    "Rollback if business dashboard public JSON",
    "Monitoring first hour JSON",
    "Monitoring first day JSON",
    "Yandex crawl monitoring JSON",
    "Google crawl monitoring JSON",
    "Server logs monitoring JSON",
    "Django errors monitoring JSON",
    "404/500 monitoring JSON",
    "Sitemap fetch monitoring JSON",
    "Robots fetch monitoring JSON",
    "LLMS fetch monitoring JSON",
    "AI reputation fetch monitoring JSON",
    "Critical paths inventory JSON",
    "Public paths inventory JSON",
    "Private paths inventory JSON",
    "Admin paths inventory JSON",
    "Machine-readable paths inventory JSON",
    "Indexable submit paths inventory JSON",
    "Noindex held paths inventory JSON",
    "Ops hub source JSON",
    "Deployment handoff HTML source JSON",
    "Release readiness source JSON",
    "Blockers JSON source JSON",
    "Blockers HTML source JSON",
    "Route smoke live source JSON",
    "Route smoke JSON source JSON",
    "Route smoke CSV source JSON",
    "No public exposure JSON",
    "No sitemap inclusion JSON",
    "Private cache safe JSON",
    "CI adapter ready JSON",
    "Cron adapter ready JSON",
    "Post-deploy automation ready JSON",
    "Manual owner required JSON",
    "Timestamp placeholder JSON",
    "Environment placeholder JSON",
    "Revision placeholder JSON",
    "Deploy actor placeholder JSON",
    "Yandex-first strategy JSON",
    "Kazakhstan construction SEO JSON",
    "Trust and neutrality JSON",
    "Evidence privacy JSON",
    "Schema safety JSON",
    "B2B identity safety JSON",
    "Review moderation safety JSON",
    "Official response safety JSON",
    "Claim profile safety JSON",
    "Freshness worklist safety JSON",
    "Indexing monitor safety JSON",
    "Webmaster checklist safety JSON",
    "Keyword map safety JSON",
    "AI evidence safety JSON",
    "Launch blockers linked JSON",
    "Deployment CSV linked JSON",
    "Deployment live linked JSON",
    "Next 300-gate production adapter queue",
]

DEPLOYMENT_CSV_GATES = [gate.replace("JSON", "CSV").replace("deployment handoff JSON export", "deployment handoff CSV export") for gate in DEPLOYMENT_JSON_GATES]
DEPLOYMENT_LIVE_GATES = [gate.replace("deployment handoff JSON export", "deployment handoff live export").replace("JSON", "LIVE") for gate in DEPLOYMENT_JSON_GATES]

EXPECTED_CSV_COLUMNS = [
    "gate_number",
    "gate",
    "section",
    "status",
    "allowed",
    "source_path",
    "manual_action",
    "launch_risk_if_fails",
]


@pytest.mark.django_db
def test_deployment_machine_bundle_requires_staff(client):
    for path in [
        "/admin/launch-qa/deployment-handoff.json",
        "/admin/launch-qa/deployment-handoff.csv",
        "/admin/launch-qa/deployment-handoff-live.json",
    ]:
        response = client.get(path)
        assert response.status_code == 302
        assert "/admin/login/" in response["Location"]


@pytest.mark.django_db
def test_deployment_handoff_json_returns_100_gate_contract(client):
    staff = get_user_model().objects.create_user(username="deploy-json", password="pass", is_staff=True)
    client.force_login(staff)

    response = client.get("/admin/launch-qa/deployment-handoff.json")

    assert response.status_code == 200
    assert response["Content-Type"] == "application/json"
    payload = response.json()
    assert payload["schema"] == "otzoviki.deployment_handoff.v1"
    assert payload["version"] == "100-gate-deployment-json"
    assert payload["count"] == 100
    assert payload["staff_only"] is True
    assert payload["robots"] == "noindex,follow"
    assert payload["generated_by"] == "launchqa.deployment_handoff_json"
    assert payload["release_phase"] == "mvp-launch-cut"
    assert payload["production_credentials_required"] is False
    assert payload["external_network_used"] is False
    assert payload["mutates_state"] is False
    assert payload["method"] == "GET"
    assert payload["go_no_go"]["status"] == "go"
    assert payload["summary"]["failed"] == 0
    assert payload["sources"]["deployment_handoff_html"] == "/admin/launch-qa/deployment-handoff/"
    assert payload["sources"]["deployment_handoff_csv"] == "/admin/launch-qa/deployment-handoff.csv"
    assert payload["sources"]["deployment_handoff_live"] == "/admin/launch-qa/deployment-handoff-live.json"
    assert len(payload["gates"]) == 100
    assert payload["gates"][0] == "100-gate deployment handoff JSON export"
    assert payload["gates"][-1] == "Next 300-gate production adapter queue"
    for gate in DEPLOYMENT_JSON_GATES:
        assert gate in payload["gates"], gate
    for key in ["pre_deploy", "deploy", "post_deploy", "search_submission", "rollback", "monitoring"]:
        assert key in payload["checklists"]
        assert payload["checklists"][key]


@pytest.mark.django_db
def test_deployment_handoff_csv_returns_100_gate_contract(client):
    staff = get_user_model().objects.create_user(username="deploy-csv", password="pass", is_staff=True)
    client.force_login(staff)

    response = client.get("/admin/launch-qa/deployment-handoff.csv")

    assert response.status_code == 200
    assert response["Content-Type"] == "text/csv; charset=utf-8"
    assert response["Content-Disposition"] == 'attachment; filename="deployment-handoff.csv"'
    rows = list(csv.DictReader(io.StringIO(response.content.decode())))
    assert len(rows) == 100
    assert list(rows[0].keys()) == EXPECTED_CSV_COLUMNS
    assert rows[0]["gate_number"] == "1"
    assert rows[-1]["gate_number"] == "100"
    gates = {row["gate"] for row in rows}
    for gate in DEPLOYMENT_CSV_GATES:
        assert gate in gates, gate
    assert any(row["source_path"] == "/admin/launch-qa/release-readiness.json" for row in rows)
    assert any(row["source_path"] == "/admin/launch-qa/deployment-handoff/" for row in rows)
    assert any(row["allowed"] == "true" for row in rows)


@pytest.mark.django_db
def test_deployment_handoff_live_returns_100_gate_contract(client):
    staff = get_user_model().objects.create_user(username="deploy-live", password="pass", is_staff=True)
    client.force_login(staff)

    response = client.get("/admin/launch-qa/deployment-handoff-live.json")

    assert response.status_code == 200
    assert response["Content-Type"] == "application/json"
    payload = response.json()
    assert payload["schema"] == "otzoviki.deployment_handoff_live.v1"
    assert payload["version"] == "100-gate-deployment-live"
    assert payload["count"] == 100
    assert payload["staff_only"] is True
    assert payload["robots"] == "noindex,follow"
    assert payload["generated_by"] == "launchqa.deployment_handoff_live"
    assert payload["summary"]["failed"] == 0
    assert payload["go_no_go"]["status"] == "go"
    assert len(payload["gates"]) == 100
    assert payload["gates"][0] == "100-gate deployment handoff live export"
    assert payload["gates"][-1] == "Next 300-gate production adapter queue"
    for gate in DEPLOYMENT_LIVE_GATES:
        assert gate in payload["gates"], gate
    assert payload["live_checks"]["release_readiness_json"]["status_code"] == 200
    assert payload["live_checks"]["deployment_handoff_html"]["status_code"] == 200
    assert payload["live_checks"]["blockers_json"]["status_code"] == 200
    assert all(check["passed"] for check in payload["live_checks"].values())


@pytest.mark.django_db
def test_deployment_machine_bundle_links_from_staff_surfaces(client):
    staff = get_user_model().objects.create_user(username="deploy-links", password="pass", is_staff=True)
    client.force_login(staff)

    for path in [
        "/admin/launch-qa/",
        "/admin/launch-qa/blockers/",
        "/admin/launch-qa/route-smoke/",
        "/admin/launch-qa/deployment-handoff/",
    ]:
        response = client.get(path)
        assert response.status_code == 200
        html = response.content.decode()
        assert "/admin/launch-qa/deployment-handoff.json" in html
        assert "/admin/launch-qa/deployment-handoff.csv" in html
        assert "/admin/launch-qa/deployment-handoff-live.json" in html
