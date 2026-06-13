import csv
import io

import pytest
from django.contrib.auth import get_user_model

P0_GUIDE_CONTENT_JSON_GATES = ['100-gate P0 guide content JSON package', 'Staff-only P0 guide content JSON', 'Stable P0 guide content JSON schema', 'Versioned P0 guide content JSON payload', 'Generated P0 guide content metadata', 'Launch freeze source linked', 'Release readiness source linked', 'Deployment handoff source linked', 'Launch ops source linked', 'Blocker source linked', 'No external network JSON', 'No credential usage JSON', 'No production mutation JSON', 'GET-only JSON', 'Operator review required JSON', 'Content evidence status JSON', 'Source path inventory JSON', 'Risk state inventory JSON', 'Allowed action inventory JSON', 'Blocked action inventory JSON', 'Guide readiness marker JSON', 'Article schema marker JSON', 'FAQPage marker JSON', 'Breadcrumb marker JSON', 'AggregateRating marker JSON', 'Review schema marker JSON', 'sameAs marker JSON', 'Sitemap readiness marker JSON', 'Robots readiness marker JSON', 'Noindex readiness marker JSON', 'Canonical marker JSON', 'Crawl status marker JSON', 'E-E-A-T marker JSON', 'Author marker JSON', 'Editor marker JSON', 'Methodology marker JSON', 'Policy marker JSON', 'Analytics marker JSON', 'Yandex Webmaster marker JSON', 'Google Search Console marker JSON', 'Completeness status JSON', 'Missing items JSON', 'Manual owner JSON', 'Manual timestamp JSON', 'Manual note JSON', 'Launch blocker integration JSON', 'Noindex safety JSON', 'Canonical safety JSON', 'Schema safety JSON', 'E-E-A-T safety JSON', 'Public route coverage JSON', 'Private route exclusion JSON', 'Admin route exclusion JSON', 'Search route exclusion JSON', 'QR route exclusion JSON', 'Lead form exclusion JSON', 'Review form exclusion JSON', 'Official response exclusion JSON', 'Claim form exclusion JSON', 'Business workspace exclusion JSON', 'CSV link marker JSON', 'LIVE link marker JSON', 'Ops link marker JSON', 'Dashboard link marker JSON', 'Machine contract marker JSON', 'Stable count marker JSON', 'Deterministic order marker JSON', 'Human handoff marker JSON', 'CI adapter marker JSON', 'Cron adapter marker JSON', 'Evidence file placeholder JSON', 'Production host placeholder JSON', 'Revision placeholder JSON', 'Actor placeholder JSON', 'Environment placeholder JSON', 'Created at placeholder JSON', 'Updated at placeholder JSON', 'Verified at placeholder JSON', 'Submitted at placeholder JSON', 'Observed at placeholder JSON', 'Green state visible JSON', 'Hold state visible JSON', 'Failed zero marker JSON', 'Go/no-go marker JSON', 'Manual release marker JSON', 'Post-deploy marker JSON', 'First index batch marker JSON', 'Yandex-first marker JSON', 'Kazakhstan construction marker JSON', 'Trust neutrality marker JSON', 'Privacy guard marker JSON', 'No private evidence leak JSON', 'No copied review marker JSON', 'No paid ranking marker JSON', 'Right-of-reply marker JSON', 'Moderation audit marker JSON', 'Representative identity marker JSON', 'Indexability gate marker JSON', 'Launch report marker JSON', 'Next 300-gate queue']
P0_GUIDE_CONTENT_CSV_GATES = ['100-gate P0 guide content CSV package', 'Staff-only P0 guide content CSV', 'Stable P0 guide content CSV schema', 'Versioned P0 guide content CSV payload', 'Generated P0 guide content metadata', 'Launch freeze source linked', 'Release readiness source linked', 'Deployment handoff source linked', 'Launch ops source linked', 'Blocker source linked', 'No external network CSV', 'No credential usage CSV', 'No production mutation CSV', 'GET-only CSV', 'Operator review required CSV', 'Content evidence status CSV', 'Source path inventory CSV', 'Risk state inventory CSV', 'Allowed action inventory CSV', 'Blocked action inventory CSV', 'Guide readiness marker CSV', 'Article schema marker CSV', 'FAQPage marker CSV', 'Breadcrumb marker CSV', 'AggregateRating marker CSV', 'Review schema marker CSV', 'sameAs marker CSV', 'Sitemap readiness marker CSV', 'Robots readiness marker CSV', 'Noindex readiness marker CSV', 'Canonical marker CSV', 'Crawl status marker CSV', 'E-E-A-T marker CSV', 'Author marker CSV', 'Editor marker CSV', 'Methodology marker CSV', 'Policy marker CSV', 'Analytics marker CSV', 'Yandex Webmaster marker CSV', 'Google Search Console marker CSV', 'Completeness status CSV', 'Missing items CSV', 'Manual owner CSV', 'Manual timestamp CSV', 'Manual note CSV', 'Launch blocker integration CSV', 'Noindex safety CSV', 'Canonical safety CSV', 'Schema safety CSV', 'E-E-A-T safety CSV', 'Public route coverage CSV', 'Private route exclusion CSV', 'Admin route exclusion CSV', 'Search route exclusion CSV', 'QR route exclusion CSV', 'Lead form exclusion CSV', 'Review form exclusion CSV', 'Official response exclusion CSV', 'Claim form exclusion CSV', 'Business workspace exclusion CSV', 'CSV link marker CSV', 'LIVE link marker CSV', 'Ops link marker CSV', 'Dashboard link marker CSV', 'Machine contract marker CSV', 'Stable count marker CSV', 'Deterministic order marker CSV', 'Human handoff marker CSV', 'CI adapter marker CSV', 'Cron adapter marker CSV', 'Evidence file placeholder CSV', 'Production host placeholder CSV', 'Revision placeholder CSV', 'Actor placeholder CSV', 'Environment placeholder CSV', 'Created at placeholder CSV', 'Updated at placeholder CSV', 'Verified at placeholder CSV', 'Submitted at placeholder CSV', 'Observed at placeholder CSV', 'Green state visible CSV', 'Hold state visible CSV', 'Failed zero marker CSV', 'Go/no-go marker CSV', 'Manual release marker CSV', 'Post-deploy marker CSV', 'First index batch marker CSV', 'Yandex-first marker CSV', 'Kazakhstan construction marker CSV', 'Trust neutrality marker CSV', 'Privacy guard marker CSV', 'No private evidence leak CSV', 'No copied review marker CSV', 'No paid ranking marker CSV', 'Right-of-reply marker CSV', 'Moderation audit marker CSV', 'Representative identity marker CSV', 'Indexability gate marker CSV', 'Launch report marker CSV', 'Next 300-gate queue']
P0_GUIDE_CONTENT_LIVE_GATES = ['100-gate P0 guide content live package', 'Staff-only P0 guide content LIVE', 'Stable P0 guide content LIVE schema', 'Versioned P0 guide content LIVE payload', 'Generated P0 guide content metadata', 'Launch freeze source linked', 'Release readiness source linked', 'Deployment handoff source linked', 'Launch ops source linked', 'Blocker source linked', 'No external network LIVE', 'No credential usage LIVE', 'No production mutation LIVE', 'GET-only LIVE', 'Operator review required LIVE', 'Content evidence status LIVE', 'Source path inventory LIVE', 'Risk state inventory LIVE', 'Allowed action inventory LIVE', 'Blocked action inventory LIVE', 'Guide readiness marker LIVE', 'Article schema marker LIVE', 'FAQPage marker LIVE', 'Breadcrumb marker LIVE', 'AggregateRating marker LIVE', 'Review schema marker LIVE', 'sameAs marker LIVE', 'Sitemap readiness marker LIVE', 'Robots readiness marker LIVE', 'Noindex readiness marker LIVE', 'Canonical marker LIVE', 'Crawl status marker LIVE', 'E-E-A-T marker LIVE', 'Author marker LIVE', 'Editor marker LIVE', 'Methodology marker LIVE', 'Policy marker LIVE', 'Analytics marker LIVE', 'Yandex Webmaster marker LIVE', 'Google Search Console marker LIVE', 'Completeness status LIVE', 'Missing items LIVE', 'Manual owner LIVE', 'Manual timestamp LIVE', 'Manual note LIVE', 'Launch blocker integration LIVE', 'Noindex safety LIVE', 'Canonical safety LIVE', 'Schema safety LIVE', 'E-E-A-T safety LIVE', 'Public route coverage LIVE', 'Private route exclusion LIVE', 'Admin route exclusion LIVE', 'Search route exclusion LIVE', 'QR route exclusion LIVE', 'Lead form exclusion LIVE', 'Review form exclusion LIVE', 'Official response exclusion LIVE', 'Claim form exclusion LIVE', 'Business workspace exclusion LIVE', 'CSV link marker LIVE', 'LIVE link marker LIVE', 'Ops link marker LIVE', 'Dashboard link marker LIVE', 'Machine contract marker LIVE', 'Stable count marker LIVE', 'Deterministic order marker LIVE', 'Human handoff marker LIVE', 'CI adapter marker LIVE', 'Cron adapter marker LIVE', 'Evidence file placeholder LIVE', 'Production host placeholder LIVE', 'Revision placeholder LIVE', 'Actor placeholder LIVE', 'Environment placeholder LIVE', 'Created at placeholder LIVE', 'Updated at placeholder LIVE', 'Verified at placeholder LIVE', 'Submitted at placeholder LIVE', 'Observed at placeholder LIVE', 'Green state visible LIVE', 'Hold state visible LIVE', 'Failed zero marker LIVE', 'Go/no-go marker LIVE', 'Manual release marker LIVE', 'Post-deploy marker LIVE', 'First index batch marker LIVE', 'Yandex-first marker LIVE', 'Kazakhstan construction marker LIVE', 'Trust neutrality marker LIVE', 'Privacy guard marker LIVE', 'No private evidence leak LIVE', 'No copied review marker LIVE', 'No paid ranking marker LIVE', 'Right-of-reply marker LIVE', 'Moderation audit marker LIVE', 'Representative identity marker LIVE', 'Indexability gate marker LIVE', 'Launch report marker LIVE', 'Next 300-gate queue']

SCHEMA_CRAWL_EEAT_JSON_GATES = ['100-gate Schema crawl E-E-A-T JSON package', 'Staff-only schema crawl E-E-A-T JSON', 'Stable schema crawl E-E-A-T JSON schema', 'Versioned schema crawl E-E-A-T JSON payload', 'Generated schema crawl E-E-A-T metadata', 'Launch freeze source linked', 'Release readiness source linked', 'Deployment handoff source linked', 'Launch ops source linked', 'Blocker source linked', 'No external network JSON', 'No credential usage JSON', 'No production mutation JSON', 'GET-only JSON', 'Operator review required JSON', 'Content evidence status JSON', 'Source path inventory JSON', 'Risk state inventory JSON', 'Allowed action inventory JSON', 'Blocked action inventory JSON', 'Guide readiness marker JSON', 'Article schema marker JSON', 'FAQPage marker JSON', 'Breadcrumb marker JSON', 'AggregateRating marker JSON', 'Review schema marker JSON', 'sameAs marker JSON', 'Sitemap readiness marker JSON', 'Robots readiness marker JSON', 'Noindex readiness marker JSON', 'Canonical marker JSON', 'Crawl status marker JSON', 'E-E-A-T marker JSON', 'Author marker JSON', 'Editor marker JSON', 'Methodology marker JSON', 'Policy marker JSON', 'Analytics marker JSON', 'Yandex Webmaster marker JSON', 'Google Search Console marker JSON', 'Completeness status JSON', 'Missing items JSON', 'Manual owner JSON', 'Manual timestamp JSON', 'Manual note JSON', 'Launch blocker integration JSON', 'Noindex safety JSON', 'Canonical safety JSON', 'Schema safety JSON', 'E-E-A-T safety JSON', 'Public route coverage JSON', 'Private route exclusion JSON', 'Admin route exclusion JSON', 'Search route exclusion JSON', 'QR route exclusion JSON', 'Lead form exclusion JSON', 'Review form exclusion JSON', 'Official response exclusion JSON', 'Claim form exclusion JSON', 'Business workspace exclusion JSON', 'CSV link marker JSON', 'LIVE link marker JSON', 'Ops link marker JSON', 'Dashboard link marker JSON', 'Machine contract marker JSON', 'Stable count marker JSON', 'Deterministic order marker JSON', 'Human handoff marker JSON', 'CI adapter marker JSON', 'Cron adapter marker JSON', 'Evidence file placeholder JSON', 'Production host placeholder JSON', 'Revision placeholder JSON', 'Actor placeholder JSON', 'Environment placeholder JSON', 'Created at placeholder JSON', 'Updated at placeholder JSON', 'Verified at placeholder JSON', 'Submitted at placeholder JSON', 'Observed at placeholder JSON', 'Green state visible JSON', 'Hold state visible JSON', 'Failed zero marker JSON', 'Go/no-go marker JSON', 'Manual release marker JSON', 'Post-deploy marker JSON', 'First index batch marker JSON', 'Yandex-first marker JSON', 'Kazakhstan construction marker JSON', 'Trust neutrality marker JSON', 'Privacy guard marker JSON', 'No private evidence leak JSON', 'No copied review marker JSON', 'No paid ranking marker JSON', 'Right-of-reply marker JSON', 'Moderation audit marker JSON', 'Representative identity marker JSON', 'Indexability gate marker JSON', 'Launch report marker JSON', 'Next 300-gate queue']
SCHEMA_CRAWL_EEAT_CSV_GATES = ['100-gate Schema crawl E-E-A-T CSV package', 'Staff-only schema crawl E-E-A-T CSV', 'Stable schema crawl E-E-A-T CSV schema', 'Versioned schema crawl E-E-A-T CSV payload', 'Generated schema crawl E-E-A-T metadata', 'Launch freeze source linked', 'Release readiness source linked', 'Deployment handoff source linked', 'Launch ops source linked', 'Blocker source linked', 'No external network CSV', 'No credential usage CSV', 'No production mutation CSV', 'GET-only CSV', 'Operator review required CSV', 'Content evidence status CSV', 'Source path inventory CSV', 'Risk state inventory CSV', 'Allowed action inventory CSV', 'Blocked action inventory CSV', 'Guide readiness marker CSV', 'Article schema marker CSV', 'FAQPage marker CSV', 'Breadcrumb marker CSV', 'AggregateRating marker CSV', 'Review schema marker CSV', 'sameAs marker CSV', 'Sitemap readiness marker CSV', 'Robots readiness marker CSV', 'Noindex readiness marker CSV', 'Canonical marker CSV', 'Crawl status marker CSV', 'E-E-A-T marker CSV', 'Author marker CSV', 'Editor marker CSV', 'Methodology marker CSV', 'Policy marker CSV', 'Analytics marker CSV', 'Yandex Webmaster marker CSV', 'Google Search Console marker CSV', 'Completeness status CSV', 'Missing items CSV', 'Manual owner CSV', 'Manual timestamp CSV', 'Manual note CSV', 'Launch blocker integration CSV', 'Noindex safety CSV', 'Canonical safety CSV', 'Schema safety CSV', 'E-E-A-T safety CSV', 'Public route coverage CSV', 'Private route exclusion CSV', 'Admin route exclusion CSV', 'Search route exclusion CSV', 'QR route exclusion CSV', 'Lead form exclusion CSV', 'Review form exclusion CSV', 'Official response exclusion CSV', 'Claim form exclusion CSV', 'Business workspace exclusion CSV', 'CSV link marker CSV', 'LIVE link marker CSV', 'Ops link marker CSV', 'Dashboard link marker CSV', 'Machine contract marker CSV', 'Stable count marker CSV', 'Deterministic order marker CSV', 'Human handoff marker CSV', 'CI adapter marker CSV', 'Cron adapter marker CSV', 'Evidence file placeholder CSV', 'Production host placeholder CSV', 'Revision placeholder CSV', 'Actor placeholder CSV', 'Environment placeholder CSV', 'Created at placeholder CSV', 'Updated at placeholder CSV', 'Verified at placeholder CSV', 'Submitted at placeholder CSV', 'Observed at placeholder CSV', 'Green state visible CSV', 'Hold state visible CSV', 'Failed zero marker CSV', 'Go/no-go marker CSV', 'Manual release marker CSV', 'Post-deploy marker CSV', 'First index batch marker CSV', 'Yandex-first marker CSV', 'Kazakhstan construction marker CSV', 'Trust neutrality marker CSV', 'Privacy guard marker CSV', 'No private evidence leak CSV', 'No copied review marker CSV', 'No paid ranking marker CSV', 'Right-of-reply marker CSV', 'Moderation audit marker CSV', 'Representative identity marker CSV', 'Indexability gate marker CSV', 'Launch report marker CSV', 'Next 300-gate queue']
SCHEMA_CRAWL_EEAT_LIVE_GATES = ['100-gate Schema crawl E-E-A-T live package', 'Staff-only schema crawl E-E-A-T LIVE', 'Stable schema crawl E-E-A-T LIVE schema', 'Versioned schema crawl E-E-A-T LIVE payload', 'Generated schema crawl E-E-A-T metadata', 'Launch freeze source linked', 'Release readiness source linked', 'Deployment handoff source linked', 'Launch ops source linked', 'Blocker source linked', 'No external network LIVE', 'No credential usage LIVE', 'No production mutation LIVE', 'GET-only LIVE', 'Operator review required LIVE', 'Content evidence status LIVE', 'Source path inventory LIVE', 'Risk state inventory LIVE', 'Allowed action inventory LIVE', 'Blocked action inventory LIVE', 'Guide readiness marker LIVE', 'Article schema marker LIVE', 'FAQPage marker LIVE', 'Breadcrumb marker LIVE', 'AggregateRating marker LIVE', 'Review schema marker LIVE', 'sameAs marker LIVE', 'Sitemap readiness marker LIVE', 'Robots readiness marker LIVE', 'Noindex readiness marker LIVE', 'Canonical marker LIVE', 'Crawl status marker LIVE', 'E-E-A-T marker LIVE', 'Author marker LIVE', 'Editor marker LIVE', 'Methodology marker LIVE', 'Policy marker LIVE', 'Analytics marker LIVE', 'Yandex Webmaster marker LIVE', 'Google Search Console marker LIVE', 'Completeness status LIVE', 'Missing items LIVE', 'Manual owner LIVE', 'Manual timestamp LIVE', 'Manual note LIVE', 'Launch blocker integration LIVE', 'Noindex safety LIVE', 'Canonical safety LIVE', 'Schema safety LIVE', 'E-E-A-T safety LIVE', 'Public route coverage LIVE', 'Private route exclusion LIVE', 'Admin route exclusion LIVE', 'Search route exclusion LIVE', 'QR route exclusion LIVE', 'Lead form exclusion LIVE', 'Review form exclusion LIVE', 'Official response exclusion LIVE', 'Claim form exclusion LIVE', 'Business workspace exclusion LIVE', 'CSV link marker LIVE', 'LIVE link marker LIVE', 'Ops link marker LIVE', 'Dashboard link marker LIVE', 'Machine contract marker LIVE', 'Stable count marker LIVE', 'Deterministic order marker LIVE', 'Human handoff marker LIVE', 'CI adapter marker LIVE', 'Cron adapter marker LIVE', 'Evidence file placeholder LIVE', 'Production host placeholder LIVE', 'Revision placeholder LIVE', 'Actor placeholder LIVE', 'Environment placeholder LIVE', 'Created at placeholder LIVE', 'Updated at placeholder LIVE', 'Verified at placeholder LIVE', 'Submitted at placeholder LIVE', 'Observed at placeholder LIVE', 'Green state visible LIVE', 'Hold state visible LIVE', 'Failed zero marker LIVE', 'Go/no-go marker LIVE', 'Manual release marker LIVE', 'Post-deploy marker LIVE', 'First index batch marker LIVE', 'Yandex-first marker LIVE', 'Kazakhstan construction marker LIVE', 'Trust neutrality marker LIVE', 'Privacy guard marker LIVE', 'No private evidence leak LIVE', 'No copied review marker LIVE', 'No paid ranking marker LIVE', 'Right-of-reply marker LIVE', 'Moderation audit marker LIVE', 'Representative identity marker LIVE', 'Indexability gate marker LIVE', 'Launch report marker LIVE', 'Next 300-gate queue']

ANALYTICS_WEBMASTER_READINESS_JSON_GATES = ['100-gate Analytics Webmaster readiness JSON package', 'Staff-only analytics webmaster readiness JSON', 'Stable analytics webmaster readiness JSON schema', 'Versioned analytics webmaster readiness JSON payload', 'Generated analytics webmaster readiness metadata', 'Launch freeze source linked', 'Release readiness source linked', 'Deployment handoff source linked', 'Launch ops source linked', 'Blocker source linked', 'No external network JSON', 'No credential usage JSON', 'No production mutation JSON', 'GET-only JSON', 'Operator review required JSON', 'Content evidence status JSON', 'Source path inventory JSON', 'Risk state inventory JSON', 'Allowed action inventory JSON', 'Blocked action inventory JSON', 'Guide readiness marker JSON', 'Article schema marker JSON', 'FAQPage marker JSON', 'Breadcrumb marker JSON', 'AggregateRating marker JSON', 'Review schema marker JSON', 'sameAs marker JSON', 'Sitemap readiness marker JSON', 'Robots readiness marker JSON', 'Noindex readiness marker JSON', 'Canonical marker JSON', 'Crawl status marker JSON', 'E-E-A-T marker JSON', 'Author marker JSON', 'Editor marker JSON', 'Methodology marker JSON', 'Policy marker JSON', 'Analytics marker JSON', 'Yandex Webmaster marker JSON', 'Google Search Console marker JSON', 'Completeness status JSON', 'Missing items JSON', 'Manual owner JSON', 'Manual timestamp JSON', 'Manual note JSON', 'Launch blocker integration JSON', 'Noindex safety JSON', 'Canonical safety JSON', 'Schema safety JSON', 'E-E-A-T safety JSON', 'Public route coverage JSON', 'Private route exclusion JSON', 'Admin route exclusion JSON', 'Search route exclusion JSON', 'QR route exclusion JSON', 'Lead form exclusion JSON', 'Review form exclusion JSON', 'Official response exclusion JSON', 'Claim form exclusion JSON', 'Business workspace exclusion JSON', 'CSV link marker JSON', 'LIVE link marker JSON', 'Ops link marker JSON', 'Dashboard link marker JSON', 'Machine contract marker JSON', 'Stable count marker JSON', 'Deterministic order marker JSON', 'Human handoff marker JSON', 'CI adapter marker JSON', 'Cron adapter marker JSON', 'Evidence file placeholder JSON', 'Production host placeholder JSON', 'Revision placeholder JSON', 'Actor placeholder JSON', 'Environment placeholder JSON', 'Created at placeholder JSON', 'Updated at placeholder JSON', 'Verified at placeholder JSON', 'Submitted at placeholder JSON', 'Observed at placeholder JSON', 'Green state visible JSON', 'Hold state visible JSON', 'Failed zero marker JSON', 'Go/no-go marker JSON', 'Manual release marker JSON', 'Post-deploy marker JSON', 'First index batch marker JSON', 'Yandex-first marker JSON', 'Kazakhstan construction marker JSON', 'Trust neutrality marker JSON', 'Privacy guard marker JSON', 'No private evidence leak JSON', 'No copied review marker JSON', 'No paid ranking marker JSON', 'Right-of-reply marker JSON', 'Moderation audit marker JSON', 'Representative identity marker JSON', 'Indexability gate marker JSON', 'Launch report marker JSON', 'Next 300-gate queue']
ANALYTICS_WEBMASTER_READINESS_CSV_GATES = ['100-gate Analytics Webmaster readiness CSV package', 'Staff-only analytics webmaster readiness CSV', 'Stable analytics webmaster readiness CSV schema', 'Versioned analytics webmaster readiness CSV payload', 'Generated analytics webmaster readiness metadata', 'Launch freeze source linked', 'Release readiness source linked', 'Deployment handoff source linked', 'Launch ops source linked', 'Blocker source linked', 'No external network CSV', 'No credential usage CSV', 'No production mutation CSV', 'GET-only CSV', 'Operator review required CSV', 'Content evidence status CSV', 'Source path inventory CSV', 'Risk state inventory CSV', 'Allowed action inventory CSV', 'Blocked action inventory CSV', 'Guide readiness marker CSV', 'Article schema marker CSV', 'FAQPage marker CSV', 'Breadcrumb marker CSV', 'AggregateRating marker CSV', 'Review schema marker CSV', 'sameAs marker CSV', 'Sitemap readiness marker CSV', 'Robots readiness marker CSV', 'Noindex readiness marker CSV', 'Canonical marker CSV', 'Crawl status marker CSV', 'E-E-A-T marker CSV', 'Author marker CSV', 'Editor marker CSV', 'Methodology marker CSV', 'Policy marker CSV', 'Analytics marker CSV', 'Yandex Webmaster marker CSV', 'Google Search Console marker CSV', 'Completeness status CSV', 'Missing items CSV', 'Manual owner CSV', 'Manual timestamp CSV', 'Manual note CSV', 'Launch blocker integration CSV', 'Noindex safety CSV', 'Canonical safety CSV', 'Schema safety CSV', 'E-E-A-T safety CSV', 'Public route coverage CSV', 'Private route exclusion CSV', 'Admin route exclusion CSV', 'Search route exclusion CSV', 'QR route exclusion CSV', 'Lead form exclusion CSV', 'Review form exclusion CSV', 'Official response exclusion CSV', 'Claim form exclusion CSV', 'Business workspace exclusion CSV', 'CSV link marker CSV', 'LIVE link marker CSV', 'Ops link marker CSV', 'Dashboard link marker CSV', 'Machine contract marker CSV', 'Stable count marker CSV', 'Deterministic order marker CSV', 'Human handoff marker CSV', 'CI adapter marker CSV', 'Cron adapter marker CSV', 'Evidence file placeholder CSV', 'Production host placeholder CSV', 'Revision placeholder CSV', 'Actor placeholder CSV', 'Environment placeholder CSV', 'Created at placeholder CSV', 'Updated at placeholder CSV', 'Verified at placeholder CSV', 'Submitted at placeholder CSV', 'Observed at placeholder CSV', 'Green state visible CSV', 'Hold state visible CSV', 'Failed zero marker CSV', 'Go/no-go marker CSV', 'Manual release marker CSV', 'Post-deploy marker CSV', 'First index batch marker CSV', 'Yandex-first marker CSV', 'Kazakhstan construction marker CSV', 'Trust neutrality marker CSV', 'Privacy guard marker CSV', 'No private evidence leak CSV', 'No copied review marker CSV', 'No paid ranking marker CSV', 'Right-of-reply marker CSV', 'Moderation audit marker CSV', 'Representative identity marker CSV', 'Indexability gate marker CSV', 'Launch report marker CSV', 'Next 300-gate queue']
ANALYTICS_WEBMASTER_READINESS_LIVE_GATES = ['100-gate Analytics Webmaster readiness live package', 'Staff-only analytics webmaster readiness LIVE', 'Stable analytics webmaster readiness LIVE schema', 'Versioned analytics webmaster readiness LIVE payload', 'Generated analytics webmaster readiness metadata', 'Launch freeze source linked', 'Release readiness source linked', 'Deployment handoff source linked', 'Launch ops source linked', 'Blocker source linked', 'No external network LIVE', 'No credential usage LIVE', 'No production mutation LIVE', 'GET-only LIVE', 'Operator review required LIVE', 'Content evidence status LIVE', 'Source path inventory LIVE', 'Risk state inventory LIVE', 'Allowed action inventory LIVE', 'Blocked action inventory LIVE', 'Guide readiness marker LIVE', 'Article schema marker LIVE', 'FAQPage marker LIVE', 'Breadcrumb marker LIVE', 'AggregateRating marker LIVE', 'Review schema marker LIVE', 'sameAs marker LIVE', 'Sitemap readiness marker LIVE', 'Robots readiness marker LIVE', 'Noindex readiness marker LIVE', 'Canonical marker LIVE', 'Crawl status marker LIVE', 'E-E-A-T marker LIVE', 'Author marker LIVE', 'Editor marker LIVE', 'Methodology marker LIVE', 'Policy marker LIVE', 'Analytics marker LIVE', 'Yandex Webmaster marker LIVE', 'Google Search Console marker LIVE', 'Completeness status LIVE', 'Missing items LIVE', 'Manual owner LIVE', 'Manual timestamp LIVE', 'Manual note LIVE', 'Launch blocker integration LIVE', 'Noindex safety LIVE', 'Canonical safety LIVE', 'Schema safety LIVE', 'E-E-A-T safety LIVE', 'Public route coverage LIVE', 'Private route exclusion LIVE', 'Admin route exclusion LIVE', 'Search route exclusion LIVE', 'QR route exclusion LIVE', 'Lead form exclusion LIVE', 'Review form exclusion LIVE', 'Official response exclusion LIVE', 'Claim form exclusion LIVE', 'Business workspace exclusion LIVE', 'CSV link marker LIVE', 'LIVE link marker LIVE', 'Ops link marker LIVE', 'Dashboard link marker LIVE', 'Machine contract marker LIVE', 'Stable count marker LIVE', 'Deterministic order marker LIVE', 'Human handoff marker LIVE', 'CI adapter marker LIVE', 'Cron adapter marker LIVE', 'Evidence file placeholder LIVE', 'Production host placeholder LIVE', 'Revision placeholder LIVE', 'Actor placeholder LIVE', 'Environment placeholder LIVE', 'Created at placeholder LIVE', 'Updated at placeholder LIVE', 'Verified at placeholder LIVE', 'Submitted at placeholder LIVE', 'Observed at placeholder LIVE', 'Green state visible LIVE', 'Hold state visible LIVE', 'Failed zero marker LIVE', 'Go/no-go marker LIVE', 'Manual release marker LIVE', 'Post-deploy marker LIVE', 'First index batch marker LIVE', 'Yandex-first marker LIVE', 'Kazakhstan construction marker LIVE', 'Trust neutrality marker LIVE', 'Privacy guard marker LIVE', 'No private evidence leak LIVE', 'No copied review marker LIVE', 'No paid ranking marker LIVE', 'Right-of-reply marker LIVE', 'Moderation audit marker LIVE', 'Representative identity marker LIVE', 'Indexability gate marker LIVE', 'Launch report marker LIVE', 'Next 300-gate queue']

EXPECTED_COLUMNS = ['gate_number', 'gate', 'section', 'status', 'allowed', 'source_path', 'manual_action', 'launch_risk_if_fails']

@pytest.mark.django_db
def test_next_three_launch_cut_packages_require_staff(client):
    for path in ['/admin/launch-qa/p0-guide-content.json', '/admin/launch-qa/p0-guide-content.csv', '/admin/launch-qa/p0-guide-content.live.json', '/admin/launch-qa/schema-crawl-eeat.json', '/admin/launch-qa/schema-crawl-eeat.csv', '/admin/launch-qa/schema-crawl-eeat.live.json', '/admin/launch-qa/analytics-webmaster-readiness.json', '/admin/launch-qa/analytics-webmaster-readiness.csv', '/admin/launch-qa/analytics-webmaster-readiness.live.json']:
        response = client.get(path)
        assert response.status_code == 302
        assert '/admin/login/' in response['Location']

@pytest.mark.django_db
def test_p0_guide_content_json_csv_live_contracts(client):
    staff = get_user_model().objects.create_user(username='p0_guide_content', password='pass', is_staff=True)
    client.force_login(staff)

    response = client.get('/admin/launch-qa/p0-guide-content.json')
    assert response.status_code == 200
    assert response['Content-Type'] == 'application/json'
    payload = response.json()
    assert payload['schema'] == 'otzoviki.p0_guide_content.v1'
    assert payload['version'] == '100-gate-p0-guide-content-json'
    assert payload['count'] == 100
    assert payload['staff_only'] is True
    assert payload['robots'] == 'noindex,follow'
    assert payload['release_phase'] == 'p0-guide-content-batch'
    assert payload['external_network_used'] is False
    assert payload['production_credentials_required'] is False
    assert payload['mutates_state'] is False
    assert payload['method'] == 'GET'
    assert payload['summary']['failed'] == 0
    assert payload['go_no_go']['status'] in ['go', 'hold']
    assert payload['links']['csv'] == '/admin/launch-qa/p0-guide-content.csv'
    assert payload['links']['live'] == '/admin/launch-qa/p0-guide-content.live.json'
    assert len(payload['gates']) == 100
    assert payload['gates'][0] == P0_GUIDE_CONTENT_JSON_GATES[0]
    assert payload['gates'][-1] == 'Next 300-gate queue'
    for gate in P0_GUIDE_CONTENT_JSON_GATES:
        assert gate in payload['gates'], gate

    response = client.get('/admin/launch-qa/p0-guide-content.csv')
    assert response.status_code == 200
    assert response['Content-Type'] == 'text/csv; charset=utf-8'
    assert response['Content-Disposition'] == 'attachment; filename="p0-guide-content.csv"'
    rows = list(csv.DictReader(io.StringIO(response.content.decode())))
    assert len(rows) == 100
    assert list(rows[0].keys()) == EXPECTED_COLUMNS
    assert rows[0]['gate_number'] == '1'
    assert rows[-1]['gate_number'] == '100'
    gates = {row['gate'] for row in rows}
    for gate in P0_GUIDE_CONTENT_CSV_GATES:
        assert gate in gates, gate
    assert any(row['source_path'] == '/admin/launch-qa/release-readiness.json' for row in rows)

    response = client.get('/admin/launch-qa/p0-guide-content.live.json')
    assert response.status_code == 200
    assert response['Content-Type'] == 'application/json'
    payload = response.json()
    assert payload['schema'] == 'otzoviki.p0_guide_content_live.v1'
    assert payload['version'] == '100-gate-p0-guide-content-live'
    assert payload['count'] == 100
    assert payload['summary']['failed'] == 0
    assert len(payload['gates']) == 100
    assert payload['gates'][0] == P0_GUIDE_CONTENT_LIVE_GATES[0]
    assert payload['gates'][-1] == 'Next 300-gate queue'
    for gate in P0_GUIDE_CONTENT_LIVE_GATES:
        assert gate in payload['gates'], gate
    assert all(check['passed'] for check in payload['live_checks'].values())

@pytest.mark.django_db
def test_schema_crawl_eeat_json_csv_live_contracts(client):
    staff = get_user_model().objects.create_user(username='schema_crawl_eeat', password='pass', is_staff=True)
    client.force_login(staff)

    response = client.get('/admin/launch-qa/schema-crawl-eeat.json')
    assert response.status_code == 200
    assert response['Content-Type'] == 'application/json'
    payload = response.json()
    assert payload['schema'] == 'otzoviki.schema_crawl_eeat.v1'
    assert payload['version'] == '100-gate-schema-crawl-eeat-json'
    assert payload['count'] == 100
    assert payload['staff_only'] is True
    assert payload['robots'] == 'noindex,follow'
    assert payload['release_phase'] == 'schema-crawl-eeat-validation'
    assert payload['external_network_used'] is False
    assert payload['production_credentials_required'] is False
    assert payload['mutates_state'] is False
    assert payload['method'] == 'GET'
    assert payload['summary']['failed'] == 0
    assert payload['go_no_go']['status'] in ['go', 'hold']
    assert payload['links']['csv'] == '/admin/launch-qa/schema-crawl-eeat.csv'
    assert payload['links']['live'] == '/admin/launch-qa/schema-crawl-eeat.live.json'
    assert len(payload['gates']) == 100
    assert payload['gates'][0] == SCHEMA_CRAWL_EEAT_JSON_GATES[0]
    assert payload['gates'][-1] == 'Next 300-gate queue'
    for gate in SCHEMA_CRAWL_EEAT_JSON_GATES:
        assert gate in payload['gates'], gate

    response = client.get('/admin/launch-qa/schema-crawl-eeat.csv')
    assert response.status_code == 200
    assert response['Content-Type'] == 'text/csv; charset=utf-8'
    assert response['Content-Disposition'] == 'attachment; filename="schema-crawl-eeat.csv"'
    rows = list(csv.DictReader(io.StringIO(response.content.decode())))
    assert len(rows) == 100
    assert list(rows[0].keys()) == EXPECTED_COLUMNS
    assert rows[0]['gate_number'] == '1'
    assert rows[-1]['gate_number'] == '100'
    gates = {row['gate'] for row in rows}
    for gate in SCHEMA_CRAWL_EEAT_CSV_GATES:
        assert gate in gates, gate
    assert any(row['source_path'] == '/admin/launch-qa/release-readiness.json' for row in rows)

    response = client.get('/admin/launch-qa/schema-crawl-eeat.live.json')
    assert response.status_code == 200
    assert response['Content-Type'] == 'application/json'
    payload = response.json()
    assert payload['schema'] == 'otzoviki.schema_crawl_eeat_live.v1'
    assert payload['version'] == '100-gate-schema-crawl-eeat-live'
    assert payload['count'] == 100
    assert payload['summary']['failed'] == 0
    assert len(payload['gates']) == 100
    assert payload['gates'][0] == SCHEMA_CRAWL_EEAT_LIVE_GATES[0]
    assert payload['gates'][-1] == 'Next 300-gate queue'
    for gate in SCHEMA_CRAWL_EEAT_LIVE_GATES:
        assert gate in payload['gates'], gate
    assert all(check['passed'] for check in payload['live_checks'].values())

@pytest.mark.django_db
def test_analytics_webmaster_readiness_json_csv_live_contracts(client):
    staff = get_user_model().objects.create_user(username='analytics_webmaster_readiness', password='pass', is_staff=True)
    client.force_login(staff)

    response = client.get('/admin/launch-qa/analytics-webmaster-readiness.json')
    assert response.status_code == 200
    assert response['Content-Type'] == 'application/json'
    payload = response.json()
    assert payload['schema'] == 'otzoviki.analytics_webmaster_readiness.v1'
    assert payload['version'] == '100-gate-analytics-webmaster-readiness-json'
    assert payload['count'] == 100
    assert payload['staff_only'] is True
    assert payload['robots'] == 'noindex,follow'
    assert payload['release_phase'] == 'analytics-webmaster-verification-readiness'
    assert payload['external_network_used'] is False
    assert payload['production_credentials_required'] is False
    assert payload['mutates_state'] is False
    assert payload['method'] == 'GET'
    assert payload['summary']['failed'] == 0
    assert payload['go_no_go']['status'] in ['go', 'hold']
    assert payload['links']['csv'] == '/admin/launch-qa/analytics-webmaster-readiness.csv'
    assert payload['links']['live'] == '/admin/launch-qa/analytics-webmaster-readiness.live.json'
    assert len(payload['gates']) == 100
    assert payload['gates'][0] == ANALYTICS_WEBMASTER_READINESS_JSON_GATES[0]
    assert payload['gates'][-1] == 'Next 300-gate queue'
    for gate in ANALYTICS_WEBMASTER_READINESS_JSON_GATES:
        assert gate in payload['gates'], gate

    response = client.get('/admin/launch-qa/analytics-webmaster-readiness.csv')
    assert response.status_code == 200
    assert response['Content-Type'] == 'text/csv; charset=utf-8'
    assert response['Content-Disposition'] == 'attachment; filename="analytics-webmaster-readiness.csv"'
    rows = list(csv.DictReader(io.StringIO(response.content.decode())))
    assert len(rows) == 100
    assert list(rows[0].keys()) == EXPECTED_COLUMNS
    assert rows[0]['gate_number'] == '1'
    assert rows[-1]['gate_number'] == '100'
    gates = {row['gate'] for row in rows}
    for gate in ANALYTICS_WEBMASTER_READINESS_CSV_GATES:
        assert gate in gates, gate
    assert any(row['source_path'] == '/admin/launch-qa/release-readiness.json' for row in rows)

    response = client.get('/admin/launch-qa/analytics-webmaster-readiness.live.json')
    assert response.status_code == 200
    assert response['Content-Type'] == 'application/json'
    payload = response.json()
    assert payload['schema'] == 'otzoviki.analytics_webmaster_readiness_live.v1'
    assert payload['version'] == '100-gate-analytics-webmaster-readiness-live'
    assert payload['count'] == 100
    assert payload['summary']['failed'] == 0
    assert len(payload['gates']) == 100
    assert payload['gates'][0] == ANALYTICS_WEBMASTER_READINESS_LIVE_GATES[0]
    assert payload['gates'][-1] == 'Next 300-gate queue'
    for gate in ANALYTICS_WEBMASTER_READINESS_LIVE_GATES:
        assert gate in payload['gates'], gate
    assert all(check['passed'] for check in payload['live_checks'].values())

@pytest.mark.django_db
def test_next_three_package_links_visible_from_ops_hub(client):
    staff = get_user_model().objects.create_user(username='next-three-package-links', password='pass', is_staff=True)
    client.force_login(staff)
    response = client.get('/admin/launch-qa/')
    assert response.status_code == 200
    html = response.content.decode()
    for link in ['/admin/launch-qa/p0-guide-content.json', '/admin/launch-qa/p0-guide-content.csv', '/admin/launch-qa/p0-guide-content.live.json', '/admin/launch-qa/schema-crawl-eeat.json', '/admin/launch-qa/schema-crawl-eeat.csv', '/admin/launch-qa/schema-crawl-eeat.live.json', '/admin/launch-qa/analytics-webmaster-readiness.json', '/admin/launch-qa/analytics-webmaster-readiness.csv', '/admin/launch-qa/analytics-webmaster-readiness.live.json']:
        assert link in html, link
