import pytest
from django.contrib.auth import get_user_model


BLOCKER_100_GATES = [
    "100-gate launch blocker dashboard",
    "Staff-only blocker dashboard",
    "Robots: noindex,follow",
    "Canonical blocker dashboard URL",
    "Live runner summary",
    "Route smoke HTML link",
    "Route smoke JSON link",
    "Route smoke CSV link",
    "Route smoke live link",
    "Ops hub back link",
    "Yandex submit blocked if failures",
    "Google submit blocked if failures",
    "Sitemap submit blocked if failures",
    "AI crawler docs blocker check",
    "Robots policy blocker check",
    "Sitemap XML blocker check",
    "LLMS TXT blocker check",
    "AI reputation markdown blocker check",
    "Public home blocker check",
    "KZ root blocker check",
    "For-business blocker check",
    "Claim-profile noindex blocker check",
    "Reputation-audit noindex blocker check",
    "Business dashboard redirect blocker check",
    "Admin ops auth blocker check",
    "Route smoke matrix auth blocker check",
    "JSON export auth blocker check",
    "CSV export auth blocker check",
    "Status code failures visible",
    "Content-type failures visible",
    "Robots marker failures visible",
    "Redirect failures visible",
    "Failed paths list visible",
    "Passed count visible",
    "Failed count visible",
    "Probe count visible",
    "Launch blocker count visible",
    "Green launch state visible",
    "Red launch state visible",
    "Manual verification reminder",
    "No external network note",
    "GET-only probe note",
    "No mutation note",
    "No production credentials note",
    "Post-deploy required note",
    "Yandex Webmaster hold note",
    "Google Search Console hold note",
    "IndexNow hold note",
    "Sitemap submission hold note",
    "Public route release gate",
    "Private route release gate",
    "Admin route release gate",
    "Machine-readable release gate",
    "Policy page release gate",
    "Lead form release gate",
    "B2B workspace release gate",
    "Search noindex release gate",
    "QR noindex release gate",
    "Evidence privacy release gate",
    "Paid neutrality release gate",
    "Right-of-reply release gate",
    "Schema safety release gate",
    "AggregateRating release gate",
    "Review schema release gate",
    "Canonical release gate",
    "Breadcrumb release gate",
    "JSON-LD release gate",
    "Sitemap inclusion release gate",
    "Sitemap exclusion release gate",
    "Robots allow release gate",
    "Robots disallow release gate",
    "Empty profile suppression gate",
    "Draft guide suppression gate",
    "Low-quality guide suppression gate",
    "Admin launch QA suppression gate",
    "Keyword admin suppression gate",
    "AI evidence admin suppression gate",
    "Business workspace suppression gate",
    "Search suppression gate",
    "QR suppression gate",
    "Review form suppression gate",
    "Official response form suppression gate",
    "Claim form suppression gate",
    "Reputation audit form suppression gate",
    "Methodology public gate",
    "Review policy public gate",
    "Right-of-reply public gate",
    "Privacy public gate",
    "Terms public gate",
    "For-business public gate",
    "Live result snippets visible",
    "Response bytes visible",
    "Launch blocker boolean visible",
    "CI scheduling source visible",
    "Cron wrapper source visible",
    "Manual owner action visible",
    "Next deploy smoke queue",
    "Next Search Console queue",
    "Next Yandex Webmaster queue",
    "Next 100-gate launch cut queue",
]


@pytest.mark.django_db
def test_launch_blocker_dashboard_requires_staff(client):
    response = client.get("/admin/launch-qa/blockers/")

    assert response.status_code == 302
    assert "/admin/login/" in response["Location"]


@pytest.mark.django_db
def test_launch_blocker_dashboard_exposes_100_gate_summary(client):
    staff = get_user_model().objects.create_user(username="blockers", password="pass", is_staff=True)
    client.force_login(staff)

    response = client.get("/admin/launch-qa/blockers/")

    assert response.status_code == 200
    html = response.content.decode()
    assert '<meta name="robots" content="noindex,follow">' in html
    assert '<link rel="canonical" href="http://testserver/admin/launch-qa/blockers/">' in html
    assert "Launch blocker dashboard" in html
    assert "Live runner summary" in html
    assert "probe_count" in html
    assert "passed" in html
    assert "failed" in html
    assert "failed_paths" in html
    assert "0 failed" in html
    for path in [
        "/admin/launch-qa/",
        "/admin/launch-qa/route-smoke/",
        "/admin/launch-qa/route-smoke.json",
        "/admin/launch-qa/route-smoke-export.csv",
        "/admin/launch-qa/route-smoke-live.json",
    ]:
        assert path in html, path
    for marker in BLOCKER_100_GATES:
        assert marker in html, marker


@pytest.mark.django_db
def test_launch_ops_and_route_smoke_link_blocker_dashboard(client):
    staff = get_user_model().objects.create_user(username="blocker-link", password="pass", is_staff=True)
    client.force_login(staff)

    for path in ["/admin/launch-qa/", "/admin/launch-qa/route-smoke/"]:
        response = client.get(path)
        assert response.status_code == 200
        assert "/admin/launch-qa/blockers/" in response.content.decode()
