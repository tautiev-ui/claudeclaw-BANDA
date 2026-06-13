import csv
import io

import pytest
from django.core.management import call_command
from django.contrib.auth import get_user_model

from apps.companies.models import Company
from apps.editorial.models import Author, EditorialPolicy, MethodologyVersion
from apps.guides.models import Guide
from apps.locations.models import City


@pytest.mark.django_db
def test_seed_launch_cut_content_creates_real_editorial_guides_and_indexable_company_depth(client):
    call_command("seed_launch_cut_content")

    assert MethodologyVersion.objects.filter(is_current=True).count() == 1
    assert EditorialPolicy.objects.filter(is_published=True).count() >= 5
    assert Author.objects.filter(role=Author.Role.AUTHOR).exists()
    assert Author.objects.filter(role=Author.Role.EDITOR).exists()
    assert Author.objects.filter(role=Author.Role.REVIEWER).exists()

    launch_ready_guides = [guide for guide in Guide.objects.all() if guide.is_launch_ready]
    assert len(launch_ready_guides) >= 4
    expected_guide_slugs = {
        "kak-proverit-remontnuyu-kompaniyu",
        "kak-vybrat-remontnuyu-kompaniyu",
        "kak-chitat-otzyvy-o-remonte",
        "kak-proverit-smetu-na-remont",
    }
    assert expected_guide_slugs.issubset(set(Guide.objects.values_list("slug", flat=True)))
    for guide in launch_ready_guides[:4]:
        assert guide.quality_issues == []
        assert guide.quality_gated_robots_meta == "index,follow"

    assert City.objects.filter(slug="almaty").exists()
    assert City.objects.filter(slug="astana").exists()
    assert Company.objects.filter(index_status="indexable").count() >= 50
    for company in Company.objects.filter(index_status="indexable")[:10]:
        company.full_clean()
        assert company.schema_eligible is True
        assert company.external_sources.filter(same_as_verified=True).exists()
        assert company.service_links.exists()

    for path in [
        "/kz/astana/",
        "/kz/astana/remont-kvartir/",
        "/kz/astana/reyting-remontnyh-kompaniy/",
        "/kz/guides/kak-proverit-remontnuyu-kompaniyu/",
    ]:
        response = client.get(path)
        assert response.status_code == 200
        assert '<meta name="robots" content="index,follow">' in response.content.decode()


@pytest.mark.django_db
def test_launch_content_completeness_csv_requires_staff_and_reports_seed_state(client):
    anonymous = client.get("/admin/launch-qa/launch-content-completeness.csv")
    assert anonymous.status_code == 302
    assert "/admin/login/" in anonymous["Location"]

    call_command("seed_launch_cut_content")
    staff = get_user_model().objects.create_user(username="content-report", password="pass", is_staff=True)
    client.force_login(staff)

    response = client.get("/admin/launch-qa/launch-content-completeness.csv")

    assert response.status_code == 200
    assert response["Content-Type"] == "text/csv; charset=utf-8"
    assert response["Content-Disposition"] == 'attachment; filename="launch-content-completeness.csv"'
    rows = list(csv.DictReader(io.StringIO(response.content.decode())))
    assert rows
    by_key = {row["check_key"]: row for row in rows}
    assert by_key["indexable_companies"]["status"] == "pass"
    assert int(by_key["indexable_companies"]["actual"]) >= 50
    assert by_key["launch_ready_guides"]["status"] == "pass"
    assert int(by_key["launch_ready_guides"]["actual"]) >= 4
    assert by_key["editorial_foundation"]["status"] == "pass"
    assert by_key["astana_depth"]["status"] == "pass"
