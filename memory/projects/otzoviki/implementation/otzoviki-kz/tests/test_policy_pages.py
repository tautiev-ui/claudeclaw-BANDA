import pytest


@pytest.mark.django_db
def test_privacy_and_terms_pages_render_indexable_policy_pages(client):
    for url, heading in [
        ("/privacy/", "Политика конфиденциальности"),
        ("/terms/", "Пользовательское соглашение"),
        ("/review-policy/", "Правила отзывов"),
        ("/right-of-reply/", "Право на ответ"),
    ]:
        response = client.get(url)

        assert response.status_code == 200
        html = response.content.decode()
        assert heading in html
        assert '<meta name="robots" content="index,follow">' in html
        assert f'<link rel="canonical" href="http://testserver{url}">' in html
        assert "BreadcrumbList" in html
        assert "персональные данные" in html.lower() or "условия" in html.lower()
        assert "Публичная политика Otzoviki KZ" in html
        assert "Что публикуется" in html
        assert "Что остаётся приватным" in html
        assert "Модерация и право на ответ" in html
        assert "Платный профиль не влияет на рейтинг" in html
