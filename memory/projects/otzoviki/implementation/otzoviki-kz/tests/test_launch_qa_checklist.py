import pytest
from django.contrib.auth import get_user_model


@pytest.mark.django_db
def test_launch_qa_checklist_requires_staff(client):
    response = client.get("/admin/launch-qa/checklist/")

    assert response.status_code == 302
    assert "/admin/login/" in response["Location"]


@pytest.mark.django_db
def test_launch_qa_checklist_seeds_launch_gate_items(client):
    from apps.launchqa.models import LaunchQACheck

    staff = get_user_model().objects.create_user(username="launch", password="pass", is_staff=True)
    client.force_login(staff)

    response = client.get("/admin/launch-qa/checklist/")

    assert response.status_code == 200
    html = response.content.decode()
    assert '<meta name="robots" content="noindex,follow">' in html
    assert "Launch QA checklist" in html
    assert "Routes and status codes" in html
    assert "Canonicals and robots meta" in html
    assert "Schema matches visible content" in html
    assert "Sitemap only contains indexable canonical URLs" in html
    assert "Mobile and CWV basics" in html
    assert "40-gate launch readiness" in html
    assert "Route smoke matrix" in html
    assert "Indexability gates" in html
    assert "Schema parity" in html
    assert "Sitemap hygiene" in html
    assert "Thin-page suppression" in html
    assert "Legal/trust pages" in html
    assert "AEO/GEO public docs" in html
    assert "B2B neutrality disclosure" in html
    assert "Block launch if failed" in html
    assert LaunchQACheck.objects.filter(category=LaunchQACheck.Category.ROUTES).exists()
    assert LaunchQACheck.objects.filter(category=LaunchQACheck.Category.INDEXABILITY).exists()
    assert LaunchQACheck.objects.filter(category=LaunchQACheck.Category.SCHEMA).exists()


@pytest.mark.django_db
def test_launch_qa_check_completion_property():
    from apps.launchqa.models import LaunchQACheck

    check = LaunchQACheck.objects.create(
        category=LaunchQACheck.Category.ROUTES,
        check_key="home-200",
        title="Home renders 200",
        target="/",
    )

    assert check.status == LaunchQACheck.Status.TODO
    assert not check.is_done

    check.status = LaunchQACheck.Status.PASSED
    check.save(update_fields=["status"])

    assert check.is_done
