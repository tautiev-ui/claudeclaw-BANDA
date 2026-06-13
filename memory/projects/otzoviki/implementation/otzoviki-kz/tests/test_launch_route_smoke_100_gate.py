import pytest
from django.contrib.auth import get_user_model


ROUTE_SMOKE_100_GATES = [
    "100-gate route smoke matrix",
    "Staff-only route QA surface",
    "Robots: noindex,follow",
    "Home route expected 200 index",
    "KZ root expected 200 index",
    "City hub populated expected index",
    "City hub empty expected noindex",
    "City service populated expected index",
    "City service empty expected noindex",
    "Ranking populated expected index",
    "Ranking empty expected noindex",
    "Price populated expected index",
    "Price empty expected noindex",
    "Company dossier trust-gated expected index",
    "Company dossier empty expected noindex",
    "Company review submission expected noindex",
    "Company official response expected noindex",
    "Guides hub populated expected index",
    "Guides hub empty expected noindex",
    "Guide detail launch-ready expected index",
    "Guide detail low-quality expected noindex",
    "Methodology expected index",
    "Review policy expected index",
    "Right-of-reply expected index",
    "Privacy expected index",
    "Terms expected index",
    "For-business expected index",
    "Claim-profile expected noindex",
    "Reputation-audit expected noindex",
    "Business root anonymous expected 302",
    "Business dashboard anonymous expected 302",
    "Business dashboard authenticated expected noindex",
    "Search expected noindex",
    "Search autocomplete expected JSON",
    "QR landing expected noindex",
    "QR platform click expected redirect",
    "Robots txt expected text/plain",
    "Sitemap expected application/xml",
    "LLMS expected text/plain",
    "AI reputation expected text/markdown",
    "Admin launch ops expected noindex",
    "Launch QA checklist expected noindex",
    "Indexing monitor expected noindex",
    "Freshness dashboard expected noindex",
    "Webmaster checklist expected noindex",
    "SEO audit CSV expected text/csv",
    "Keyword report expected noindex",
    "Keyword page-map CSV expected text/csv",
    "AI evidence capture expected noindex",
    "Admin app expected staff-only",
    "Canonical tag required for HTML public pages",
    "Canonical absent OK for machine-readable docs",
    "BreadcrumbList required for SEO HTML pages",
    "JSON-LD validity check required",
    "AggregateRating only on visible review pages",
    "Review schema only for owned visible reviews",
    "Noindex pages excluded from sitemap",
    "Private routes excluded from sitemap",
    "QR routes excluded from sitemap",
    "Search routes excluded from sitemap",
    "Admin routes excluded from sitemap",
    "Lead forms excluded from sitemap",
    "Official-response forms excluded from sitemap",
    "Review forms excluded from sitemap",
    "Draft companies excluded from sitemap",
    "Draft guides excluded from sitemap",
    "Low-quality guides excluded from sitemap",
    "Empty city pages excluded from sitemap",
    "Empty service pages excluded from sitemap",
    "Empty ranking pages excluded from sitemap",
    "Empty price pages excluded from sitemap",
    "Same-host canonical expected",
    "No query strings in canonical",
    "No fragments in canonical",
    "Robots allow public AI docs",
    "Robots disallow admin launch QA",
    "Robots disallow admin keywords",
    "Robots disallow admin AI evidence",
    "Robots disallow business workspace",
    "Robots disallow search",
    "Robots disallow QR routes",
    "Status code matrix visible",
    "Robots expectation matrix visible",
    "Canonical expectation matrix visible",
    "Schema expectation matrix visible",
    "Sitemap expectation matrix visible",
    "Auth expectation matrix visible",
    "Indexability reason visible",
    "Launch risk reason visible",
    "Manual probe note visible",
    "Staff should validate after deploy",
    "Yandex Webmaster submit only green routes",
    "Google Search Console submit only green routes",
    "AI crawler docs must remain public",
    "Private evidence must remain private",
    "Paid profile neutrality route check",
    "Right-of-reply route check",
    "B2B identity route check",
    "Moderation admin route check",
    "Next route-smoke export queue",
]


@pytest.mark.django_db
def test_launch_route_smoke_matrix_requires_staff(client):
    response = client.get("/admin/launch-qa/route-smoke/")

    assert response.status_code == 302
    assert "/admin/login/" in response["Location"]


@pytest.mark.django_db
def test_launch_route_smoke_matrix_exposes_100_route_gates(client):
    staff = get_user_model().objects.create_user(username="route-smoke", password="pass", is_staff=True)
    client.force_login(staff)

    response = client.get("/admin/launch-qa/route-smoke/")

    assert response.status_code == 200
    html = response.content.decode()
    assert '<meta name="robots" content="noindex,follow">' in html
    assert '<link rel="canonical" href="http://testserver/admin/launch-qa/route-smoke/">' in html
    for path in [
        "/",
        "/kz/",
        "/kz/almaty/",
        "/kz/almaty/remont-kvartir/",
        "/kz/almaty/reyting-remontnyh-kompaniy/",
        "/kz/almaty/remont-kvartir/ceny/",
        "/kz/company/{slug}/",
        "/kz/guides/",
        "/methodology/",
        "/review-policy/",
        "/right-of-reply/",
        "/privacy/",
        "/terms/",
        "/for-business/",
        "/claim-profile/",
        "/reputation-audit/",
        "/business/dashboard/",
        "/search/",
        "/robots.txt",
        "/sitemap.xml",
        "/llms.txt",
        "/ai-reputation.md",
        "/admin/launch-qa/",
    ]:
        assert path in html, path
    for marker in ROUTE_SMOKE_100_GATES:
        assert marker in html, marker


@pytest.mark.django_db
def test_launch_ops_hub_links_route_smoke_matrix(client):
    staff = get_user_model().objects.create_user(username="ops-route-smoke", password="pass", is_staff=True)
    client.force_login(staff)

    response = client.get("/admin/launch-qa/")

    assert response.status_code == 200
    assert "/admin/launch-qa/route-smoke/" in response.content.decode()
