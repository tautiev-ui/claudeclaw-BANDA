import pytest
from django.contrib.auth import get_user_model


DEPLOYMENT_HANDOFF_100_GATES = [
    "100-gate deployment handoff dashboard",
    "Staff-only deployment surface",
    "Robots: noindex,follow",
    "Canonical deployment handoff URL",
    "Release readiness source linked",
    "Blocker JSON source linked",
    "Blocker dashboard source linked",
    "Route smoke live source linked",
    "Route smoke JSON source linked",
    "Route smoke CSV source linked",
    "Ops hub source linked",
    "Go/no-go status visible",
    "Summary failed count visible",
    "Launch blocker count visible",
    "Manual release required visible",
    "Post-deploy smoke required visible",
    "Pre-deploy backup reminder",
    "Pre-deploy environment variable reminder",
    "Pre-deploy static collect reminder",
    "Pre-deploy migrations reminder",
    "Pre-deploy secrets not exposed reminder",
    "Pre-deploy DEBUG false reminder",
    "Pre-deploy ALLOWED_HOSTS reminder",
    "Pre-deploy CSRF trusted origins reminder",
    "Pre-deploy database connectivity reminder",
    "Deploy code revision reminder",
    "Deploy dependency install reminder",
    "Deploy migrate command reminder",
    "Deploy collectstatic command reminder",
    "Deploy restart app service reminder",
    "Deploy restart worker service reminder",
    "Deploy health endpoint reminder",
    "Deploy run route smoke live runner",
    "Deploy verify release readiness JSON",
    "Post-deploy home probe",
    "Post-deploy KZ root probe",
    "Post-deploy for-business probe",
    "Post-deploy claim-profile noindex probe",
    "Post-deploy reputation-audit noindex probe",
    "Post-deploy business dashboard auth probe",
    "Post-deploy robots.txt probe",
    "Post-deploy sitemap.xml probe",
    "Post-deploy llms.txt probe",
    "Post-deploy ai-reputation.md probe",
    "Post-deploy ops hub probe",
    "Post-deploy blockers probe",
    "Post-deploy release-readiness probe",
    "Yandex Webmaster submit only after green",
    "Google Search Console submit only after green",
    "IndexNow only after green",
    "Do not submit noindex URLs",
    "Do not submit admin URLs",
    "Do not submit search URLs",
    "Do not submit QR URLs",
    "Do not submit lead form URLs",
    "Do not submit private business URLs",
    "Sitemap only canonical indexable URLs",
    "Robots disallow admin launch QA",
    "Robots disallow keywords admin",
    "Robots disallow AI evidence admin",
    "Robots disallow business workspace",
    "Robots allow llms.txt",
    "Robots allow ai-reputation.md",
    "AI docs remain public",
    "Blockers JSON remains private",
    "Release readiness JSON remains private",
    "Route smoke exports remain private",
    "No production credentials in handoff",
    "No external publication by app",
    "No destructive data action",
    "Rollback if blockers appear",
    "Rollback if 5xx appears",
    "Rollback if sitemap is malformed",
    "Rollback if robots blocks public docs",
    "Rollback if noindex disappears from private routes",
    "Rollback if schema safety fails",
    "Rollback if paid neutrality copy missing",
    "Rollback if review forms indexable",
    "Rollback if business dashboard public",
    "Monitoring first hour reminder",
    "Monitoring first day reminder",
    "Yandex crawling observation reminder",
    "Google crawling observation reminder",
    "Server logs review reminder",
    "Django errors review reminder",
    "404/500 review reminder",
    "Sitemap fetch review reminder",
    "Robots fetch review reminder",
    "LLMS fetch review reminder",
    "AI reputation fetch review reminder",
    "Manual owner checklist visible",
    "Deployment command checklist visible",
    "Post-deploy smoke checklist visible",
    "Search submission checklist visible",
    "Rollback checklist visible",
    "Monitoring checklist visible",
    "Green release state visible",
    "Red hold state visible",
    "Next deployment JSON queue",
    "Next production cron queue",
]


@pytest.mark.django_db
def test_deployment_handoff_requires_staff(client):
    response = client.get("/admin/launch-qa/deployment-handoff/")

    assert response.status_code == 302
    assert "/admin/login/" in response["Location"]


@pytest.mark.django_db
def test_deployment_handoff_exposes_100_gate_manual_release_dashboard(client):
    staff = get_user_model().objects.create_user(username="deploy-handoff", password="pass", is_staff=True)
    client.force_login(staff)

    response = client.get("/admin/launch-qa/deployment-handoff/")

    assert response.status_code == 200
    html = response.content.decode()
    assert '<meta name="robots" content="noindex,follow">' in html
    assert '<link rel="canonical" href="http://testserver/admin/launch-qa/deployment-handoff/">' in html
    for path in [
        "/admin/launch-qa/release-readiness.json",
        "/admin/launch-qa/blockers.json",
        "/admin/launch-qa/blockers/",
        "/admin/launch-qa/route-smoke-live.json",
        "/admin/launch-qa/route-smoke.json",
        "/admin/launch-qa/route-smoke-export.csv",
        "/admin/launch-qa/",
    ]:
        assert path in html, path
    for marker in [
        "status: go",
        "failed: 0",
        "launch_blocker_count: 0",
        "manual_release_required: True",
        "post_deploy_smoke_required: True",
        "Run post-deploy route smoke live runner",
        "Submit green sitemap to Yandex Webmaster",
        "Submit green sitemap to Google Search Console",
        "Run IndexNow only after green state",
        "Rollback or hold release if any blocker appears",
    ]:
        assert marker in html, marker
    for marker in DEPLOYMENT_HANDOFF_100_GATES:
        assert marker in html, marker


@pytest.mark.django_db
def test_ops_pages_link_deployment_handoff(client):
    staff = get_user_model().objects.create_user(username="deploy-handoff-link", password="pass", is_staff=True)
    client.force_login(staff)

    for path in ["/admin/launch-qa/", "/admin/launch-qa/blockers/", "/admin/launch-qa/route-smoke/"]:
        response = client.get(path)
        assert response.status_code == 200
        assert "/admin/launch-qa/deployment-handoff/" in response.content.decode()
