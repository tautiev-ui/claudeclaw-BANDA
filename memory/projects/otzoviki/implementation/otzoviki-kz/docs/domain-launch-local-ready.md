# Domain launch local-ready handoff

This is the final local-only handoff before attaching a real domain/origin. It performs no deploy, DNS/CDN mutation, Webmaster/GSC action, IndexNow call, or credential handling.

## Current local state

- Verified company first-index batch: `docs/search-submission-package/verified-company-first-index-batch.csv`
- Production preflight runner: `deploy/scripts/run_verified_first_index_preflight.py`
- Staff-only HTML endpoint: `/admin/launch-qa/verified-company-first-index-batch/`
- Staff-only CSV endpoint: `/admin/launch-qa/verified-company-first-index-batch.csv`
- Local production-like smoke target used during handoff: `http://127.0.0.1:8027`

## Local production-like commands

Use a long real secret in production. The value below is local-only.

```bash
export DJANGO_SETTINGS_MODULE=config.settings.prod
export DJANGO_SECRET_KEY='local-production-like-secret-0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ-not-for-deploy'
export DJANGO_DEBUG=false
export DJANGO_ALLOWED_HOSTS='localhost,127.0.0.1,testserver'
export DJANGO_SECURE_SSL_REDIRECT=false
export DJANGO_SECURE_HSTS_PRELOAD=false
export DATABASE_URL='sqlite:///db.sqlite3'

python manage.py migrate --check
python manage.py check
python manage.py check --deploy
python manage.py collectstatic --noinput --dry-run
python manage.py runserver 127.0.0.1:8027
```

Expected local `check --deploy` warning: `security.W021` while `DJANGO_SECURE_HSTS_PRELOAD=false`. Keep preload false until HTTPS is stable and preload submission is intentional.

## Production environment decisions

Set these outside the repository:

```bash
DJANGO_SETTINGS_MODULE=config.settings.prod
DJANGO_SECRET_KEY=<long-random-secret-from-secret-manager>
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=<domain>,www.<domain>
DJANGO_SECURE_SSL_REDIRECT=true
DJANGO_SECURE_HSTS_SECONDS=3600
DJANGO_SECURE_HSTS_PRELOAD=false
DATABASE_URL=postgres://<user>:<password>@<host>:5432/<database>
REDIS_URL=redis://127.0.0.1:6379/0
MEILISEARCH_URL=http://127.0.0.1:7700
MEILISEARCH_MASTER_KEY=<set-in-secret-manager>
```

## After domain/origin is live

Run the preflight against the real domain:

```bash
python deploy/scripts/run_verified_first_index_preflight.py \
  --base-url https://<domain> \
  --batch-csv docs/search-submission-package/verified-company-first-index-batch.csv \
  --output-dir var/production-preflight-<domain>
```

Manual submission is allowed only if:

- `batch_pass=26/26`
- `forbidden_pass=10/10`
- public company pages have no CAPTCHA, auth wall, JS challenge, or bot block
- sitemap and robots are fetched from the real domain
- operator fills the submission evidence log

## GO/HOLD rules

GO only when all are true:

1. DNS resolves for apex and/or `www` production host.
2. HTTP redirects and HTTPS terminate correctly.
3. `python manage.py check --deploy` has no unexpected warning beyond the accepted HSTS preload hold.
4. 26 verified company URLs pass preflight on the real domain.
5. 10 forbidden URL probes pass on the real domain.
6. No admin/search/forms/private/QR/noindex URLs are submitted.

HOLD if any URL has 3xx unexpected redirect, 4xx/5xx, missing `index,follow`, canonical mismatch, missing Yandex/2GIS link, missing company name, or DNS/HTTP failure.
