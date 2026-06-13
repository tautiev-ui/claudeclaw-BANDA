from pathlib import Path

from django.core.management.base import BaseCommand

RUNBOOK = """# Production launch runbook

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
"""

FIRST_BATCH = """# First index batch

This batch is the first controlled set of URLs allowed for Yandex Webmaster, Google Search Console and IndexNow submission after production smoke passes.

Rules:

- do not submit noindex pages;
- do not submit search, claim-profile, B2B forms, QR, admin, private workspace, or empty profiles;
- submit only pages that return 200 and `index,follow` on the production origin;
- run `python manage.py seed_launch_cut_content` and `python manage.py run_launch_cut_crawl` before exporting;
- use `/admin/launch-qa/first-index-batch.csv` as the staff-only export.

Manual systems:

- Yandex Webmaster: verify site, submit sitemap, then submit first batch if available.
- Google Search Console: verify property, submit sitemap, inspect first batch samples.
- IndexNow: verify key outside repo, submit first batch only after production smoke.
"""


class Command(BaseCommand):
    help = "Write production launch runbook and first-index batch handoff docs."

    def handle(self, *args, **options):
        docs_dir = Path("docs")
        docs_dir.mkdir(exist_ok=True)
        (docs_dir / "production-launch-runbook.md").write_text(RUNBOOK)
        (docs_dir / "first-index-batch.md").write_text(FIRST_BATCH)
        self.stdout.write(self.style.SUCCESS("Prepared production launch runbook and first-index batch docs."))
