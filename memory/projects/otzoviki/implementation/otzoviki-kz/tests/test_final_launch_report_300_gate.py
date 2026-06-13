import csv
import io

import pytest
from django.contrib.auth import get_user_model

FINAL_LAUNCH_REPORT_JSON_GATES = ['100-gate Final launch report JSON package', 'Staff-only final launch report JSON', 'Stable final launch report JSON schema', 'Versioned final launch report JSON payload', 'Generated final launch report metadata', 'Launch freeze source linked', 'Release readiness source linked', 'Deployment handoff source linked', 'Launch ops source linked', 'Blocker source linked', 'No external network JSON', 'No credential usage JSON', 'No production mutation JSON', 'GET-only JSON', 'Operator review required JSON', 'CDN settings marker JSON', 'Cloudflare conservative marker JSON', 'DNS-only fallback marker JSON', 'Bunny CDN fallback marker JSON', 'Origin direct marker JSON', 'Googlebot fetch marker JSON', 'YandexBot fetch marker JSON', 'Public HTML marker JSON', 'No JS challenge marker JSON', 'No CAPTCHA marker JSON', 'Admin protection marker JSON', 'Private noindex marker JSON', 'Sitemap fetch marker JSON', 'Robots fetch marker JSON', 'LLMS fetch marker JSON', 'AI reputation fetch marker JSON', 'Data completeness source JSON', 'P0 guide source JSON', 'Schema crawl source JSON', 'Analytics source JSON', 'Webmaster source JSON', 'Submission evidence source JSON', 'Editorial foundation source JSON', 'Launch data source JSON', 'Go/no-go rollup JSON', 'Completeness status JSON', 'Missing items JSON', 'Manual owner JSON', 'Manual timestamp JSON', 'Manual note JSON', 'Launch blocker integration JSON', 'Noindex safety JSON', 'Canonical safety JSON', 'Schema safety JSON', 'E-E-A-T safety JSON', 'Public route coverage JSON', 'Private route exclusion JSON', 'Admin route exclusion JSON', 'Search route exclusion JSON', 'QR route exclusion JSON', 'Lead form exclusion JSON', 'Review form exclusion JSON', 'Official response exclusion JSON', 'Claim form exclusion JSON', 'Business workspace exclusion JSON', 'CSV link marker JSON', 'LIVE link marker JSON', 'Ops link marker JSON', 'Dashboard link marker JSON', 'Machine contract marker JSON', 'Stable count marker JSON', 'Deterministic order marker JSON', 'Human handoff marker JSON', 'CI adapter marker JSON', 'Cron adapter marker JSON', 'Evidence file placeholder JSON', 'Production host placeholder JSON', 'Revision placeholder JSON', 'Actor placeholder JSON', 'Environment placeholder JSON', 'Created at placeholder JSON', 'Updated at placeholder JSON', 'Verified at placeholder JSON', 'Submitted at placeholder JSON', 'Observed at placeholder JSON', 'Green state visible JSON', 'Hold state visible JSON', 'Failed zero marker JSON', 'Go/no-go marker JSON', 'Manual release marker JSON', 'Post-deploy marker JSON', 'First index batch marker JSON', 'Yandex-first marker JSON', 'Kazakhstan construction marker JSON', 'Trust neutrality marker JSON', 'Privacy guard marker JSON', 'No private evidence leak JSON', 'No copied review marker JSON', 'No paid ranking marker JSON', 'Right-of-reply marker JSON', 'Moderation audit marker JSON', 'Representative identity marker JSON', 'Indexability gate marker JSON', 'Launch report marker JSON', 'End of frozen launch-cut gates']
FINAL_LAUNCH_REPORT_CSV_GATES = ['100-gate Final launch report CSV package', 'Staff-only final launch report CSV', 'Stable final launch report CSV schema', 'Versioned final launch report CSV payload', 'Generated final launch report metadata', 'Launch freeze source linked', 'Release readiness source linked', 'Deployment handoff source linked', 'Launch ops source linked', 'Blocker source linked', 'No external network CSV', 'No credential usage CSV', 'No production mutation CSV', 'GET-only CSV', 'Operator review required CSV', 'CDN settings marker CSV', 'Cloudflare conservative marker CSV', 'DNS-only fallback marker CSV', 'Bunny CDN fallback marker CSV', 'Origin direct marker CSV', 'Googlebot fetch marker CSV', 'YandexBot fetch marker CSV', 'Public HTML marker CSV', 'No JS challenge marker CSV', 'No CAPTCHA marker CSV', 'Admin protection marker CSV', 'Private noindex marker CSV', 'Sitemap fetch marker CSV', 'Robots fetch marker CSV', 'LLMS fetch marker CSV', 'AI reputation fetch marker CSV', 'Data completeness source CSV', 'P0 guide source CSV', 'Schema crawl source CSV', 'Analytics source CSV', 'Webmaster source CSV', 'Submission evidence source CSV', 'Editorial foundation source CSV', 'Launch data source CSV', 'Go/no-go rollup CSV', 'Completeness status CSV', 'Missing items CSV', 'Manual owner CSV', 'Manual timestamp CSV', 'Manual note CSV', 'Launch blocker integration CSV', 'Noindex safety CSV', 'Canonical safety CSV', 'Schema safety CSV', 'E-E-A-T safety CSV', 'Public route coverage CSV', 'Private route exclusion CSV', 'Admin route exclusion CSV', 'Search route exclusion CSV', 'QR route exclusion CSV', 'Lead form exclusion CSV', 'Review form exclusion CSV', 'Official response exclusion CSV', 'Claim form exclusion CSV', 'Business workspace exclusion CSV', 'CSV link marker CSV', 'LIVE link marker CSV', 'Ops link marker CSV', 'Dashboard link marker CSV', 'Machine contract marker CSV', 'Stable count marker CSV', 'Deterministic order marker CSV', 'Human handoff marker CSV', 'CI adapter marker CSV', 'Cron adapter marker CSV', 'Evidence file placeholder CSV', 'Production host placeholder CSV', 'Revision placeholder CSV', 'Actor placeholder CSV', 'Environment placeholder CSV', 'Created at placeholder CSV', 'Updated at placeholder CSV', 'Verified at placeholder CSV', 'Submitted at placeholder CSV', 'Observed at placeholder CSV', 'Green state visible CSV', 'Hold state visible CSV', 'Failed zero marker CSV', 'Go/no-go marker CSV', 'Manual release marker CSV', 'Post-deploy marker CSV', 'First index batch marker CSV', 'Yandex-first marker CSV', 'Kazakhstan construction marker CSV', 'Trust neutrality marker CSV', 'Privacy guard marker CSV', 'No private evidence leak CSV', 'No copied review marker CSV', 'No paid ranking marker CSV', 'Right-of-reply marker CSV', 'Moderation audit marker CSV', 'Representative identity marker CSV', 'Indexability gate marker CSV', 'Launch report marker CSV', 'End of frozen launch-cut gates']
FINAL_LAUNCH_REPORT_LIVE_GATES = ['100-gate Final launch report live package', 'Staff-only final launch report LIVE', 'Stable final launch report LIVE schema', 'Versioned final launch report LIVE payload', 'Generated final launch report metadata', 'Launch freeze source linked', 'Release readiness source linked', 'Deployment handoff source linked', 'Launch ops source linked', 'Blocker source linked', 'No external network LIVE', 'No credential usage LIVE', 'No production mutation LIVE', 'GET-only LIVE', 'Operator review required LIVE', 'CDN settings marker LIVE', 'Cloudflare conservative marker LIVE', 'DNS-only fallback marker LIVE', 'Bunny CDN fallback marker LIVE', 'Origin direct marker LIVE', 'Googlebot fetch marker LIVE', 'YandexBot fetch marker LIVE', 'Public HTML marker LIVE', 'No JS challenge marker LIVE', 'No CAPTCHA marker LIVE', 'Admin protection marker LIVE', 'Private noindex marker LIVE', 'Sitemap fetch marker LIVE', 'Robots fetch marker LIVE', 'LLMS fetch marker LIVE', 'AI reputation fetch marker LIVE', 'Data completeness source LIVE', 'P0 guide source LIVE', 'Schema crawl source LIVE', 'Analytics source LIVE', 'Webmaster source LIVE', 'Submission evidence source LIVE', 'Editorial foundation source LIVE', 'Launch data source LIVE', 'Go/no-go rollup LIVE', 'Completeness status LIVE', 'Missing items LIVE', 'Manual owner LIVE', 'Manual timestamp LIVE', 'Manual note LIVE', 'Launch blocker integration LIVE', 'Noindex safety LIVE', 'Canonical safety LIVE', 'Schema safety LIVE', 'E-E-A-T safety LIVE', 'Public route coverage LIVE', 'Private route exclusion LIVE', 'Admin route exclusion LIVE', 'Search route exclusion LIVE', 'QR route exclusion LIVE', 'Lead form exclusion LIVE', 'Review form exclusion LIVE', 'Official response exclusion LIVE', 'Claim form exclusion LIVE', 'Business workspace exclusion LIVE', 'CSV link marker LIVE', 'LIVE link marker LIVE', 'Ops link marker LIVE', 'Dashboard link marker LIVE', 'Machine contract marker LIVE', 'Stable count marker LIVE', 'Deterministic order marker LIVE', 'Human handoff marker LIVE', 'CI adapter marker LIVE', 'Cron adapter marker LIVE', 'Evidence file placeholder LIVE', 'Production host placeholder LIVE', 'Revision placeholder LIVE', 'Actor placeholder LIVE', 'Environment placeholder LIVE', 'Created at placeholder LIVE', 'Updated at placeholder LIVE', 'Verified at placeholder LIVE', 'Submitted at placeholder LIVE', 'Observed at placeholder LIVE', 'Green state visible LIVE', 'Hold state visible LIVE', 'Failed zero marker LIVE', 'Go/no-go marker LIVE', 'Manual release marker LIVE', 'Post-deploy marker LIVE', 'First index batch marker LIVE', 'Yandex-first marker LIVE', 'Kazakhstan construction marker LIVE', 'Trust neutrality marker LIVE', 'Privacy guard marker LIVE', 'No private evidence leak LIVE', 'No copied review marker LIVE', 'No paid ranking marker LIVE', 'Right-of-reply marker LIVE', 'Moderation audit marker LIVE', 'Representative identity marker LIVE', 'Indexability gate marker LIVE', 'Launch report marker LIVE', 'End of frozen launch-cut gates']

EXPECTED_COLUMNS = ['gate_number', 'gate', 'section', 'status', 'allowed', 'source_path', 'manual_action', 'launch_risk_if_fails']

@pytest.mark.django_db
def test_final_launch_report_requires_staff(client):
    for path in ['/admin/launch-qa/final-launch-report.json', '/admin/launch-qa/final-launch-report.csv', '/admin/launch-qa/final-launch-report.live.json']:
        response = client.get(path)
        assert response.status_code == 302
        assert '/admin/login/' in response['Location']

@pytest.mark.django_db
def test_final_launch_report_json_csv_live_contracts(client):
    staff = get_user_model().objects.create_user(username='final-launch-report', password='pass', is_staff=True)
    client.force_login(staff)
    response = client.get('/admin/launch-qa/final-launch-report.json')
    assert response.status_code == 200
    assert response['Content-Type'] == 'application/json'
    payload = response.json()
    assert payload['schema'] == 'otzoviki.final_launch_report.v1'
    assert payload['version'] == '100-gate-final-launch-report-json'
    assert payload['count'] == 100
    assert payload['staff_only'] is True
    assert payload['robots'] == 'noindex,follow'
    assert payload['release_phase'] == 'cdn-origin-bot-qa-final-launch-report'
    assert payload['external_network_used'] is False
    assert payload['production_credentials_required'] is False
    assert payload['mutates_state'] is False
    assert payload['method'] == 'GET'
    assert payload['summary']['failed'] == 0
    assert payload['go_no_go']['status'] in ['go', 'hold']
    assert payload['launch_cut']['completed_through'] == 'OTZ-3922'
    assert payload['launch_cut']['remaining_gates'] == 0
    assert payload['launch_cut']['frozen_scope_complete'] is True
    assert payload['links']['csv'] == '/admin/launch-qa/final-launch-report.csv'
    assert payload['links']['live'] == '/admin/launch-qa/final-launch-report.live.json'
    assert len(payload['gates']) == 100
    assert payload['gates'][0] == FINAL_LAUNCH_REPORT_JSON_GATES[0]
    assert payload['gates'][-1] == 'End of frozen launch-cut gates'
    for gate in FINAL_LAUNCH_REPORT_JSON_GATES:
        assert gate in payload['gates'], gate
    for key in ['submission_evidence', 'editorial_foundation', 'launch_data_completeness', 'p0_guide_content', 'schema_crawl_eeat', 'analytics_webmaster_readiness']:
        assert key in payload['rollup_sources']
    response = client.get('/admin/launch-qa/final-launch-report.csv')
    assert response.status_code == 200
    assert response['Content-Type'] == 'text/csv; charset=utf-8'
    assert response['Content-Disposition'] == 'attachment; filename="final-launch-report.csv"'
    rows = list(csv.DictReader(io.StringIO(response.content.decode())))
    assert len(rows) == 100
    assert list(rows[0].keys()) == EXPECTED_COLUMNS
    assert rows[0]['gate_number'] == '1'
    assert rows[-1]['gate_number'] == '100'
    gates = {row['gate'] for row in rows}
    for gate in FINAL_LAUNCH_REPORT_CSV_GATES:
        assert gate in gates, gate
    assert any(row['source_path'] == '/admin/launch-qa/release-readiness.json' for row in rows)
    response = client.get('/admin/launch-qa/final-launch-report.live.json')
    assert response.status_code == 200
    assert response['Content-Type'] == 'application/json'
    payload = response.json()
    assert payload['schema'] == 'otzoviki.final_launch_report_live.v1'
    assert payload['version'] == '100-gate-final-launch-report-live'
    assert payload['count'] == 100
    assert payload['summary']['failed'] == 0
    assert payload['launch_cut']['remaining_gates'] == 0
    assert len(payload['gates']) == 100
    assert payload['gates'][0] == FINAL_LAUNCH_REPORT_LIVE_GATES[0]
    assert payload['gates'][-1] == 'End of frozen launch-cut gates'
    for gate in FINAL_LAUNCH_REPORT_LIVE_GATES:
        assert gate in payload['gates'], gate
    assert all(check['passed'] for check in payload['live_checks'].values())

@pytest.mark.django_db
def test_final_launch_report_links_visible_from_ops_hub(client):
    staff = get_user_model().objects.create_user(username='final-launch-links', password='pass', is_staff=True)
    client.force_login(staff)
    response = client.get('/admin/launch-qa/')
    assert response.status_code == 200
    html = response.content.decode()
    for link in ['/admin/launch-qa/final-launch-report.json', '/admin/launch-qa/final-launch-report.csv', '/admin/launch-qa/final-launch-report.live.json']:
        assert link in html, link
