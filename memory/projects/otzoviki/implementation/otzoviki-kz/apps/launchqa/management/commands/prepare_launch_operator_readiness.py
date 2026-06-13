from pathlib import Path

from django.core.management.base import BaseCommand

from apps.launchqa.models import ensure_default_launch_qa_checks, ensure_default_webmaster_tasks

DOC = """# Launch origin / CDN / bot QA

This document is a manual-safe launch handoff. It stores no credentials and performs no external submissions.

## Cloudflare DNS-only fallback

Keep a documented path to switch Cloudflare to DNS-only if proxy, WAF or bot settings block public SEO pages.

## Conservative CDN rules

- No JS Challenge on public SEO pages.
- No CAPTCHA on public SEO pages.
- No aggressive bot fight mode for Googlebot/YandexBot public fetches.
- Admin/private protection is handled by Django auth and noindex rules, not crawler-facing challenges.

## YandexBot-like fetch

Before index release, manually fetch public routes with a YandexBot-like user agent from the production origin and verify HTML 200 plus indexable meta only where expected.

## Googlebot-like fetch

Before index release, manually fetch public routes with a Googlebot-like user agent from the production origin and verify HTML 200 plus canonical and robots parity.

## Bunny CDN secondary fallback

If Cloudflare proxy causes crawlability issues, keep Bunny CDN as a secondary static/cache fallback while origin remains directly functional.
"""


class Command(BaseCommand):
    help = "Prepare manual-safe launch operator readiness tasks and origin/CDN/bot QA documentation."

    def handle(self, *args, **options):
        ensure_default_webmaster_tasks()
        ensure_default_launch_qa_checks()
        docs_dir = Path("docs")
        docs_dir.mkdir(exist_ok=True)
        (docs_dir / "launch-origin-cdn-bot-qa.md").write_text(DOC)
        self.stdout.write(self.style.SUCCESS("Prepared launch operator readiness tasks and docs/launch-origin-cdn-bot-qa.md."))
