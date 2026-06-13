import pytest
from django.contrib.auth import get_user_model


OPS_100_GATES = [
    "100-gate launch operations hub",
    "Staff-only operations surface",
    "Robots: noindex,follow",
    "Launch QA checklist",
    "Indexing monitor",
    "Freshness dashboard",
    "Webmaster checklist",
    "SEO audit CSV export",
    "Keyword/page mapping report",
    "Keyword page-map CSV export",
    "AI evidence capture",
    "Admin moderation index",
    "Review moderation queue",
    "Official response moderation queue",
    "Claim profile moderation queue",
    "Reputation audit leads",
    "Business representative verification",
    "Company indexability review",
    "Company freshness review",
    "Private proof audit",
    "Evidence visibility audit",
    "Rating snapshot rebuild check",
    "Sitemap inclusion audit",
    "Robots policy audit",
    "LLMS public docs audit",
    "AI reputation docs audit",
    "Yandex-first readiness",
    "Google Search Console readiness",
    "Bing/AI crawler readiness",
    "Sitemap submission status",
    "Manual indexing queue",
    "Coverage diagnostics",
    "Submitted URL inventory",
    "Indexed URL inventory",
    "Noindex URL inventory",
    "Empty profile suppression",
    "HTTP 404/5xx launch risk",
    "Indexed empty profile risk",
    "Submitted noindex risk",
    "Canonical mismatch risk",
    "Schema parity risk",
    "AggregateRating safety",
    "Review schema safety",
    "Public-only evidence safety",
    "Private/admin-only evidence safety",
    "Paid profile neutrality",
    "No review deletion privilege",
    "No rating override privilege",
    "No indexing override privilege",
    "Official response separation",
    "Right-of-reply policy",
    "Claim profile approval audit",
    "Official response publish audit",
    "Reputation audit output audit",
    "Same-host source attribution",
    "External referer suppression",
    "Query/fragment stripping",
    "B2B verified identity source",
    "POST identity spoof protection",
    "Anonymous representative spoof protection",
    "Pending representative action lock",
    "Unverified email action lock",
    "Managed company actions",
    "Private workspace noindex",
    "Business dashboard live probe",
    "Company dossier live probe",
    "Guides hub live probe",
    "Guide detail quality gate",
    "Policy pages live probe",
    "Claim-profile form noindex",
    "Reputation-audit form noindex",
    "Official-response form noindex",
    "Review submission form noindex",
    "Search results noindex",
    "QR routes noindex",
    "Launch route smoke matrix",
    "Status code matrix",
    "Canonical matrix",
    "BreadcrumbList matrix",
    "JSON-LD validity matrix",
    "Mobile/CWV basics",
    "Thin-page suppression",
    "Low-quality guide suppression",
    "Draft guide suppression",
    "Draft company suppression",
    "Stale dossier worklist",
    "Stale source worklist",
    "Stale guide worklist",
    "90-day trust cutoff",
    "Yandex/AI evidence recrawl",
    "Methodology version drift",
    "Content source requirements",
    "Money-page internal links",
    "Checklist/risk/FAQ guide quality",
    "Stage 4A keyword coverage",
    "Markin page-map alignment",
    "Hybrid matrix P0/P1 coverage",
    "E-E-A-T trust gates",
    "CIS CDN fallback readiness",
    "Launch blocker summary",
    "Next 100-gate batch queue",
]


@pytest.mark.django_db
def test_launch_ops_hub_requires_staff(client):
    response = client.get("/admin/launch-qa/")

    assert response.status_code == 302
    assert "/admin/login/" in response["Location"]


@pytest.mark.django_db
def test_launch_ops_hub_exposes_100_gate_launch_operations_matrix(client):
    staff = get_user_model().objects.create_user(username="ops", password="pass", is_staff=True)
    client.force_login(staff)

    response = client.get("/admin/launch-qa/")

    assert response.status_code == 200
    html = response.content.decode()
    assert '<meta name="robots" content="noindex,follow">' in html
    assert '<link rel="canonical" href="http://testserver/admin/launch-qa/">' in html
    assert "/admin/launch-qa/checklist/" in html
    assert "/admin/launch-qa/indexing-monitor/" in html
    assert "/admin/launch-qa/freshness/" in html
    assert "/admin/launch-qa/webmaster-checklist/" in html
    assert "/admin/launch-qa/seo-audit-export.csv" in html
    assert "/admin/keywords/report/" in html
    assert "/admin/keywords/page-map-export.csv" in html
    assert "/admin/ai-evidence/capture/" in html
    assert "/business/dashboard/" in html
    assert "/robots.txt" in html
    assert "/sitemap.xml" in html
    assert "/llms.txt" in html
    assert "/ai-reputation.md" in html
    for marker in OPS_100_GATES:
        assert marker in html, marker
