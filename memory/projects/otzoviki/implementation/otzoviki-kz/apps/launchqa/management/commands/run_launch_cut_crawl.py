from django.core.management.base import BaseCommand
from django.test import Client
from django.utils import timezone

from apps.launchqa.models import IndexingMonitorURL


LAUNCH_CRAWL_TARGETS = [
    ("/", "public_indexable", "index,follow", 200),
    ("/kz/", "public_indexable", "index,follow", 200),
    ("/kz/almaty/", "public_indexable", "index,follow", 200),
    ("/kz/astana/", "public_indexable", "index,follow", 200),
    ("/kz/almaty/remont-kvartir/", "public_indexable", "index,follow", 200),
    ("/kz/astana/remont-kvartir/", "public_indexable", "index,follow", 200),
    ("/kz/almaty/reyting-remontnyh-kompaniy/", "public_indexable", "index,follow", 200),
    ("/kz/astana/reyting-remontnyh-kompaniy/", "public_indexable", "index,follow", 200),
    ("/kz/guides/", "public_indexable", "index,follow", 200),
    ("/kz/guides/kak-proverit-remontnuyu-kompaniyu/", "public_indexable", "index,follow", 200),
    ("/methodology/", "public_indexable", "index,follow", 200),
    ("/review-policy/", "public_indexable", "index,follow", 200),
    ("/right-of-reply/", "public_indexable", "index,follow", 200),
    ("/privacy/", "public_indexable", "index,follow", 200),
    ("/terms/", "public_indexable", "index,follow", 200),
    ("/for-business/", "public_indexable", "index,follow", 200),
    ("/claim-profile/", "public_noindex", "noindex,follow", 200),
    ("/reputation-audit/", "public_noindex", "noindex,follow", 200),
    ("/search/", "public_noindex", "noindex,follow", 200),
    ("/business/dashboard/", "private_noindex", "noindex,follow", 302),
]


def extract_robots(response):
    body = response.content.decode(errors="ignore")
    marker = '<meta name="robots" content="'
    if marker not in body:
        return ""
    return body.split(marker, 1)[1].split('"', 1)[0]


class Command(BaseCommand):
    help = "Run an internal Django Client launch-cut crawl and store IndexingMonitorURL rows."

    def handle(self, *args, **options):
        client = Client()
        now = timezone.now()
        errors = 0
        for path, page_type, expected_robots, expected_status in LAUNCH_CRAWL_TARGETS:
            response = client.get(path)
            robots = extract_robots(response) if response.status_code == 200 else expected_robots
            passed = response.status_code == expected_status and robots == expected_robots
            if response.status_code >= 400 or not passed:
                index_status = IndexingMonitorURL.IndexStatus.ERROR
                errors += 1
            elif expected_robots == "noindex,follow":
                index_status = IndexingMonitorURL.IndexStatus.NOINDEX
            else:
                index_status = IndexingMonitorURL.IndexStatus.DISCOVERED
            notes = f"expected_status={expected_status}; expected_robots={expected_robots}; actual_robots={robots}; passed={passed}"
            IndexingMonitorURL.objects.update_or_create(
                url=path,
                defaults={
                    "page_type": page_type,
                    "index_status": index_status,
                    "http_status": response.status_code,
                    "is_empty_profile": False,
                    "last_checked_at": now,
                    "notes": notes,
                },
            )
        self.stdout.write(self.style.SUCCESS(f"Launch crawl completed with {errors} errors across {len(LAUNCH_CRAWL_TARGETS)} URLs."))
