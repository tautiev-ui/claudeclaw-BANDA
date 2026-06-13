import csv
import io
from pathlib import Path

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command


@pytest.mark.django_db
def test_prepare_production_launch_handoff_writes_runbook_and_first_index_docs():
    call_command("prepare_production_launch_handoff")

    runbook = Path("docs/production-launch-runbook.md")
    first_batch = Path("docs/first-index-batch.md")
    assert runbook.exists()
    assert first_batch.exists()
    runbook_body = runbook.read_text()
    first_batch_body = first_batch.read_text()
    assert "python manage.py migrate" in runbook_body
    assert "python manage.py collectstatic --noinput" in runbook_body
    assert "python manage.py seed_launch_cut_content" in runbook_body
    assert "python manage.py run_launch_cut_crawl" in runbook_body
    assert "Yandex Webmaster" in first_batch_body
    assert "IndexNow" in first_batch_body
    assert "do not submit noindex" in first_batch_body.lower()


@pytest.mark.django_db
def test_first_index_batch_csv_is_staff_only_and_exports_controlled_batch(client):
    anonymous = client.get("/admin/launch-qa/first-index-batch.csv")
    assert anonymous.status_code == 302
    assert "/admin/login/" in anonymous["Location"]

    call_command("seed_launch_cut_content")
    staff = get_user_model().objects.create_user(username="first-index", password="pass", is_staff=True)
    client.force_login(staff)

    response = client.get("/admin/launch-qa/first-index-batch.csv")

    assert response.status_code == 200
    assert response["Content-Type"] == "text/csv; charset=utf-8"
    assert response["Content-Disposition"] == 'attachment; filename="first-index-batch.csv"'
    rows = list(csv.DictReader(io.StringIO(response.content.decode())))
    assert len(rows) >= 60
    assert {"url", "page_type", "priority", "robots_expected", "submission_allowed", "manual_required", "notes"}.issubset(rows[0].keys())
    by_url = {row["url"]: row for row in rows}
    for url in [
        "/kz/",
        "/kz/almaty/",
        "/kz/astana/",
        "/kz/almaty/remont-kvartir/",
        "/kz/astana/remont-kvartir/",
        "/kz/almaty/reyting-remontnyh-kompaniy/",
        "/kz/astana/reyting-remontnyh-kompaniy/",
        "/kz/guides/kak-proverit-remontnuyu-kompaniyu/",
    ]:
        assert by_url[url]["submission_allowed"] == "true"
        assert by_url[url]["robots_expected"] == "index,follow"
    company_rows = [row for row in rows if row["page_type"] == "company"]
    assert len(company_rows) >= 50
    assert all(row["submission_allowed"] == "true" for row in company_rows)
    assert not any("claim-profile" in row["url"] or "search" in row["url"] for row in rows)
