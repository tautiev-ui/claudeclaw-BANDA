#!/usr/bin/env python3
"""Manual-safe verified first-index preflight runner.

No external submission is performed. The script only fetches the provided host,
checks the staff-approved verified-company batch URLs, and writes CSV/MD reports.

Usage:
  python run_verified_first_index_preflight.py \
    --base-url https://example.kz \
    --batch-csv verified-company-first-index-batch.csv \
    --output-dir ./preflight-output
"""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path
from urllib.parse import urljoin

import requests

FORBIDDEN_PATHS = [
    ("/admin/launch-qa/verified-company-first-index-batch.csv", "staff_export", "must_redirect_or_forbidden_anonymous"),
    ("/admin/launch-qa/verified-company-first-index-batch/", "staff_export_html", "must_redirect_or_forbidden_anonymous"),
    ("/admin/", "admin", "must_redirect_or_forbidden_anonymous"),
    ("/search/", "search", "must_not_submit"),
    ("/claim-profile/", "claim_form", "must_not_submit"),
    ("/reputation-audit/", "lead_form", "must_not_submit"),
    ("/business/", "private_workspace", "must_not_submit"),
    ("/kz/company/dom-masterov/reviews/new/", "review_form", "must_not_submit"),
    ("/kz/company/dom-masterov/official-response/new/", "official_response_form", "must_not_submit"),
    ("/r/test-token/", "qr_landing", "must_not_submit"),
]


def meta_robots(text: str) -> str:
    match = re.search(r'<meta[^>]+name=["\']robots["\'][^>]*content=["\']([^"\']+)', text, re.I)
    return match.group(1).strip() if match else ""


def canonical_href(text: str) -> str:
    match = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]*href=["\']([^"\']+)', text, re.I)
    return match.group(1).strip() if match else ""


def same_canonical(canonical: str, url: str, canonical_path: str) -> bool:
    return canonical == url or canonical.endswith(url) or canonical.endswith(canonical_path)


def probe_batch(base_url: str, batch_rows: list[dict[str, str]], timeout: int) -> list[dict[str, str]]:
    out = []
    for row in batch_rows:
        url = row["url"]
        try:
            response = requests.get(urljoin(base_url, url), timeout=timeout, allow_redirects=False)
            text = response.text
            robots = meta_robots(text)
            canonical = canonical_href(text)
            yandex_ok = row["yandex_url"] in text
            two_gis_ok = row["two_gis_url"] in text
            name_ok = row["name"].lower() in text.lower()
            ok = (
                response.status_code == 200
                and robots == "index,follow"
                and same_canonical(canonical, url, row["canonical_path"])
                and yandex_ok
                and two_gis_ok
                and name_ok
            )
            blockers = []
            if response.status_code != 200:
                blockers.append(f"http_{response.status_code}")
            if robots != "index,follow":
                blockers.append(f"robots_{robots or 'missing'}")
            if not same_canonical(canonical, url, row["canonical_path"]):
                blockers.append(f"canonical_{canonical or 'missing'}")
            if not yandex_ok:
                blockers.append("missing_yandex_link")
            if not two_gis_ok:
                blockers.append("missing_2gis_link")
            if not name_ok:
                blockers.append("missing_name")
            out.append({
                "url": url,
                "name": row["name"],
                "status_code": str(response.status_code),
                "robots": robots,
                "canonical": canonical,
                "yandex_link_ok": str(yandex_ok).lower(),
                "two_gis_link_ok": str(two_gis_ok).lower(),
                "name_ok": str(name_ok).lower(),
                "bytes": str(len(text)),
                "preflight_status": "pass" if ok else "hold",
                "blockers": ";".join(blockers),
                "manual_submission_allowed_after_prod_smoke": str(ok).lower(),
            })
        except Exception as exc:  # noqa: BLE001 - operator report should capture exact blocker
            out.append({
                "url": url,
                "name": row.get("name", ""),
                "status_code": "error",
                "robots": "",
                "canonical": "",
                "yandex_link_ok": "false",
                "two_gis_link_ok": "false",
                "name_ok": "false",
                "bytes": "0",
                "preflight_status": "hold",
                "blockers": f"{type(exc).__name__}:{exc}",
                "manual_submission_allowed_after_prod_smoke": "false",
            })
    return out


def probe_forbidden(base_url: str, timeout: int) -> list[dict[str, str]]:
    out = []
    for path, page_type, rule in FORBIDDEN_PATHS:
        try:
            response = requests.get(urljoin(base_url, path), timeout=timeout, allow_redirects=False)
            robots = meta_robots(response.text)
            if rule == "must_redirect_or_forbidden_anonymous":
                ok = response.status_code in (302, 403)
                reason = "anonymous protected" if ok else "not protected"
            else:
                ok = response.status_code in (200, 302, 404) and robots != "index,follow"
                reason = "excluded from submission" if ok else "indexable forbidden path"
            out.append({
                "url": path,
                "page_type": page_type,
                "status_code": str(response.status_code),
                "robots": robots,
                "submission_allowed": "false",
                "check_status": "pass" if ok else "hold",
                "reason": reason,
            })
        except Exception as exc:  # noqa: BLE001 - operator report should capture exact blocker
            out.append({
                "url": path,
                "page_type": page_type,
                "status_code": "error",
                "robots": "",
                "submission_allowed": "false",
                "check_status": "hold",
                "reason": f"{type(exc).__name__}:{exc}",
            })
    return out


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, base_url: str, batch: list[dict[str, str]], forbidden: list[dict[str, str]]) -> None:
    batch_pass = sum(1 for row in batch if row["preflight_status"] == "pass")
    forbidden_pass = sum(1 for row in forbidden if row["check_status"] == "pass")
    with path.open("w", encoding="utf-8") as handle:
        handle.write(f"# Verified company first-index production preflight\n\n")
        handle.write(f"Base URL: `{base_url}`\n\n")
        handle.write(f"- Batch pass: {batch_pass}/{len(batch)}\n")
        handle.write(f"- Forbidden pass: {forbidden_pass}/{len(forbidden)}\n")
        handle.write("- External submission performed: no\n\n")
        handle.write("## Submit only if all batch rows pass\n\n")
        for row in batch:
            handle.write(f"- [{row['preflight_status']}] `{row['url']}` — HTTP {row['status_code']} — robots `{row['robots']}` — blockers `{row['blockers']}`\n")
        handle.write("\n## Forbidden probes\n\n")
        for row in forbidden:
            handle.write(f"- [{row['check_status']}] `{row['url']}` — HTTP {row['status_code']} — robots `{row['robots']}` — {row['reason']}\n")
        handle.write("\n## Boundary\n\nNo Yandex Webmaster, GSC, IndexNow, deploy, DNS/CDN, or credential action is performed by this runner.\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--batch-csv", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--timeout", type=int, default=15)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    batch_rows = list(csv.DictReader(Path(args.batch_csv).open(encoding="utf-8")))
    batch = probe_batch(args.base_url.rstrip("/") + "/", batch_rows, args.timeout)
    forbidden = probe_forbidden(args.base_url.rstrip("/") + "/", args.timeout)

    write_csv(output_dir / "production-preflight.csv", batch)
    write_csv(output_dir / "forbidden-url-check.csv", forbidden)
    write_markdown(output_dir / "production-preflight-report.md", args.base_url.rstrip("/"), batch, forbidden)

    batch_pass = sum(1 for row in batch if row["preflight_status"] == "pass")
    forbidden_pass = sum(1 for row in forbidden if row["check_status"] == "pass")
    print(f"batch_pass={batch_pass}/{len(batch)} forbidden_pass={forbidden_pass}/{len(forbidden)} output_dir={output_dir}")
    return 0 if batch_pass == len(batch) and forbidden_pass == len(forbidden) else 2


if __name__ == "__main__":
    raise SystemExit(main())
