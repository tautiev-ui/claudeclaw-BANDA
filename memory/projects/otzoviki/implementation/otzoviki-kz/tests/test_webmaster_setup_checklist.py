import pytest
from django.contrib.auth import get_user_model


@pytest.mark.django_db
def test_webmaster_setup_checklist_requires_staff(client):
    response = client.get("/admin/launch-qa/webmaster-checklist/")

    assert response.status_code == 302
    assert "/admin/login/" in response["Location"]


@pytest.mark.django_db
def test_webmaster_setup_checklist_seeds_google_and_yandex_tasks(client):
    from apps.launchqa.models import WebmasterSetupTask

    staff = get_user_model().objects.create_user(username="qa", password="pass", is_staff=True)
    WebmasterSetupTask.objects.create(
        platform=WebmasterSetupTask.Platform.YANDEX,
        task_key="external-verification-url",
        title="External verification URL",
        verification_url="https://webmaster.yandex.ru/sites/example/",
    )
    client.force_login(staff)

    response = client.get("/admin/launch-qa/webmaster-checklist/")

    assert response.status_code == 200
    html = response.content.decode()
    assert '<meta name="robots" content="noindex,follow">' in html
    assert "Yandex Webmaster" in html
    assert "Google Search Console" in html
    assert "Добавить и подтвердить сайт" in html
    assert "Отправить sitemap.xml" in html
    assert "Проверить robots.txt" in html
    assert 'href="https://webmaster.yandex.ru/sites/example/" rel="nofollow noopener noreferrer" target="_blank"' in html
    assert "40-gate webmaster readiness" in html
    assert "Yandex-first launch" in html
    assert "Google Search Console parity" in html
    assert "Bing/AI readiness" in html
    assert "Verification meta tags" in html
    assert "Sitemap submission" in html
    assert "Robots and noindex audit" in html
    assert "Manual indexing queue" in html
    assert "Coverage diagnostics" in html
    assert "Do not submit thin pages" in html
    assert WebmasterSetupTask.objects.filter(platform=WebmasterSetupTask.Platform.YANDEX).count() >= 3
    assert WebmasterSetupTask.objects.filter(platform=WebmasterSetupTask.Platform.GOOGLE).count() >= 3


@pytest.mark.django_db
def test_webmaster_setup_task_completion_status_is_explicit():
    from apps.launchqa.models import WebmasterSetupTask

    task = WebmasterSetupTask.objects.create(
        platform=WebmasterSetupTask.Platform.YANDEX,
        task_key="verify-site",
        title="Добавить и подтвердить сайт",
    )

    assert task.status == WebmasterSetupTask.Status.TODO
    assert not task.is_done

    task.status = WebmasterSetupTask.Status.DONE
    task.save(update_fields=["status"])

    assert task.is_done
