# Production launch runbook

Manual-safe runbook for moving the verified Otzoviki KZ launch-cut from local/staging to production. Do not store secrets in this document.

## 1. Release sanity

```bash
git status
pytest -q
python manage.py check
```

## 2. Deploy application

Run with the production environment and secret manager already configured:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

## 3. Seed verified launch content

```bash
python manage.py seed_launch_cut_content
python manage.py run_launch_cut_crawl
python manage.py prepare_launch_operator_readiness
python manage.py prepare_production_launch_handoff
```

## 4. Production smoke

Verify health, robots, sitemap, first-index pages, staff-only launch QA exports, and no JS/CAPTCHA challenge on public SEO pages.

## 5. Manual external submissions

Only after production smoke passes: Yandex Webmaster, Google Search Console, sitemap submit, IndexNow key verification and first batch submit. Keep credentials outside repository.
