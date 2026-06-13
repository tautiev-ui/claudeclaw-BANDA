import json
from pathlib import Path
from urllib.parse import urlparse

from django.core.management.base import BaseCommand

from apps.launchqa.launch_cut_views import _first_index_batch_rows


class Command(BaseCommand):
    help = "Export manual-safe first-index submission files for Yandex Webmaster, GSC and IndexNow. No external network calls."

    def add_arguments(self, parser):
        parser.add_argument("--output-dir", default="docs/search-submission-package")
        parser.add_argument("--host", default="https://otzoviki.kz")

    def handle(self, *args, **options):
        output_dir = Path(options["output_dir"])
        host = options["host"].rstrip("/")
        parsed = urlparse(host)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("--host must be an absolute http(s) URL")
        output_dir.mkdir(parents=True, exist_ok=True)
        rows = [row for row in _first_index_batch_rows() if row["submission_allowed"] == "true" and row["robots_expected"] == "index,follow"]
        urls = [f"{host}{row['url']}" for row in rows]

        header = "# Manual submission file. Do not submit forbidden private or noindex pages.\n"
        (output_dir / "yandex_webmaster_first_batch.txt").write_text(header + "\n".join(urls) + "\n")
        (output_dir / "gsc_first_index_batch.txt").write_text(header + "\n".join(urls) + "\n")
        payload = {
            "host": parsed.netloc,
            "key": "<set-indexnow-key-outside-repo>",
            "keyLocation": f"{host}/<set-indexnow-key-outside-repo>.txt",
            "urlList": urls,
        }
        (output_dir / "indexnow_payload.sample.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        (output_dir / "robots_sitemap_validation.md").write_text(f"""# Robots / Sitemap Validation Notes

Host: `{host}`

Before manual submission:

1. Fetch `{host}/robots.txt` from production.
2. Fetch `{host}/sitemap.xml` from production.
3. Confirm every URL in `yandex_webmaster_first_batch.txt` returns `200` and `<meta name="robots" content="index,follow">`.
4. Confirm no `/search/`, `/claim-profile/`, `/admin/`, private workspace, QR redirect, or noindex pages are present.
5. Submit manually in Yandex Webmaster / Google Search Console / IndexNow only after production smoke passes.
""")
        (output_dir / "MANIFEST.md").write_text(f"""# Search Submission Package

Generated for `{host}` with {len(urls)} first-index URLs.

Files:

- `yandex_webmaster_first_batch.txt` — manual Yandex Webmaster URL list.
- `gsc_first_index_batch.txt` — manual Google Search Console sample/list.
- `indexnow_payload.sample.json` — sample payload with placeholder key only.
- `robots_sitemap_validation.md` — pre-submit validation checklist.

No external network calls were made by this command.
""")
        self.stdout.write(self.style.SUCCESS(f"Exported {len(urls)} manual submission URLs to {output_dir}"))
