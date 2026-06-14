import pytest


def test_health_endpoint(client):
    response = client.get('/health/')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


@pytest.mark.django_db
def test_home_renders(client):
    response = client.get('/')
    body = response.content.decode('utf-8')
    assert response.status_code == 200
    assert 'Найдите надёжную ремонтную компанию' in body
    assert 'otz-search-form' in body
    assert 'Платный профиль ≠ рейтинг' in body


def test_robots_txt(client):
    response = client.get('/robots.txt')
    assert response.status_code == 200
    assert 'Disallow: /admin/' in response.content.decode('utf-8')


@pytest.mark.django_db
def test_layout_partials_render(client):
    response = client.get('/')
    body = response.content.decode('utf-8')
    for expected in [
        'otz-site-header',
        'otz-footer',
        'otz-evidence-card',
        'otz-right-of-reply',
        'otz-risk-block',
        'otz-guide-checklist',
        'otz-company-card',
    ]:
        assert expected in body
