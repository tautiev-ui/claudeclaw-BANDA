import json
from pathlib import Path

import pytest
from django.core.management import call_command


@pytest.mark.django_db
def test_export_search_submission_package_writes_manual_safe_files(tmp_path):
    call_command("seed_launch_cut_content")
    out_dir = tmp_path / "submission"

    call_command("export_search_submission_package", output_dir=str(out_dir), host="https://otzoviki.kz")

    yandex = out_dir / "yandex_webmaster_first_batch.txt"
    gsc = out_dir / "gsc_first_index_batch.txt"
    indexnow = out_dir / "indexnow_payload.sample.json"
    validation = out_dir / "robots_sitemap_validation.md"
    manifest = out_dir / "MANIFEST.md"
    for path in [yandex, gsc, indexnow, validation, manifest]:
        assert path.exists(), path
        body = path.read_text()
        assert "<set-indexnow-key-outside-repo>" in body or "otzoviki.kz" in body

    for path in [yandex, gsc, indexnow]:
        body = path.read_text()
        assert "/claim-profile/" not in body
        assert "/search/" not in body
        assert "/admin/" not in body

    urls = [line for line in yandex.read_text().splitlines() if line.startswith("https://")]
    assert len(urls) >= 60
    assert all(url.startswith("https://otzoviki.kz/") for url in urls)
    payload = json.loads(indexnow.read_text())
    assert payload["host"] == "otzoviki.kz"
    assert payload["key"] == "<set-indexnow-key-outside-repo>"
    assert len(payload["urlList"]) == len(urls)
    assert all("claim-profile" not in url and "search" not in url for url in payload["urlList"])
