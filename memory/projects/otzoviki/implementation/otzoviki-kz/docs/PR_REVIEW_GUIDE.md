# Otzoviki KZ PR Review Guide

This guide helps review the large Otzoviki KZ implementation PR in safe slices.

## Suggested review order

1. **Project skeleton and settings**
   - `config/settings/*`, `config/urls.py`, `pyproject.toml`, `.env.example`, `docker-compose.yml`.
   - Confirm secret-safe placeholders and ignored local state.

2. **SEO/indexability foundation**
   - `apps/seo/*`, sitemap/robots/llms views, schema builders, indexability tests.
   - Confirm noindex/index rules match launch gates.

3. **Public SSR pages**
   - `apps/pages/views.py`, templates under `templates/pages/` and `templates/partials/`.
   - Confirm visible content matches schema and sitemap expectations.

4. **Reviews, evidence and moderation**
   - `apps/reviews`, `apps/evidence`, `apps/ai_evidence`, moderation admin tests.
   - Confirm public/private evidence boundaries and append-only logs.

5. **B2B / right-of-reply flows**
   - `apps/business`, source attribution, claim-profile and official response moderation.
   - Confirm same-host referer handling and audit logs.

6. **Launch QA and first-index package**
   - `apps/launchqa`, deployment/launch-cut commands, staff-only CSV/JSON endpoints.
   - Confirm anonymous users are redirected and exports are GET-only/non-mutating.

7. **Markin execution layer**
   - `apps/keywords`, Markin next-wave and relevance block exports.
   - Confirm page maps support Stage 6/7/8 work without creating thin indexable pages.

8. **Operational handoff**
   - `deploy/`, `docs/production-launch-runbook.md`, `docs/production-rollback-runbook.md`.
   - Confirm all credentials are placeholders and manual external submissions remain manual.

## Local verification

```bash
cd memory/projects/otzoviki/implementation/otzoviki-kz
python -m venv .venv
. .venv/bin/activate
python -m pip install "Django>=5.0,<5.3" "psycopg[binary]>=3.2" "redis>=5" "meilisearch>=0.31" "django-environ>=0.11" "whitenoise>=6.7" "gunicorn>=22" "pytest>=8" "pytest-django>=4.8"
python manage.py check
pytest -q
```

## PR split plan if maintainers prefer smaller reviews

- PR A: skeleton/settings/public SSR baseline.
- PR B: SEO/indexability/sitemap/schema.
- PR C: reviews/evidence/moderation.
- PR D: B2B/claim/right-of-reply flows.
- PR E: launch QA, launch-cut reports and first-index batch.
- PR F: Markin next-wave, company import and deploy handoff.
