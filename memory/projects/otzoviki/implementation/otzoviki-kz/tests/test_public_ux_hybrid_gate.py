import pytest

from tests.test_home_kz_city_hub_pages import seed_local_mvp


PUBLIC_ROUTES = [
    "/",
    "/kz/",
    "/kz/almaty/",
    "/kz/almaty/remont-kvartir/",
    "/kz/almaty/reyting-remontnyh-kompaniy/",
    "/kz/company/alma-remont/",
]

INTERNAL_JARGON = [
    "MVP",
    "SEO-first",
    "SSR",
    "KZ root",
    "city service",
    "ranking</div>",
    "Business CTA",
    "Review intelligence",
    "External footprint",
    "Trust summary",
    "Shortlist action",
    "rating snapshot",
    "AI notes",
    "AI reputation notes",
    "Launch-ready",
    "Guide checklist",
    "Путь как у нормального marketplace",
]


@pytest.mark.django_db
def test_public_routes_have_visible_breadcrumbs_back_link_and_clear_next_step(client):
    seed_local_mvp()

    for path in PUBLIC_ROUTES:
        response = client.get(path)
        assert response.status_code == 200, path
        html = response.content.decode()
        assert 'data-breadcrumbs="true"' in html, path
        assert 'data-back-link="true"' in html, path
        assert 'data-next-step="true"' in html, path
        assert "Назад" in html, path


@pytest.mark.django_db
def test_public_routes_do_not_expose_internal_operator_or_tech_jargon(client):
    seed_local_mvp()

    for path in PUBLIC_ROUTES:
        response = client.get(path)
        html = response.content.decode()
        for forbidden in INTERNAL_JARGON:
            assert forbidden not in html, f"{path} exposes {forbidden!r}"


@pytest.mark.django_db
def test_hybrid_required_elements_remain_visible_after_usability_pass(client):
    seed_local_mvp()

    home = client.get("/").content.decode()
    assert "Компания или услуга" in home
    assert "Города Казахстана" in home
    assert "Проверенные досье" in home
    assert "Для компаний" in home
    assert "Как пользоваться" in home
    assert "Запросите смету только после проверки" in home
    assert "Методология" in home

    kz = client.get("/kz/").content.decode()
    assert "Выберите город" in kz
    assert "Что можно проверить" in kz
    assert "Как считается рейтинг" in kz
    assert "Популярные досье" in kz
    assert "Яндекс, 2ГИС и Google" in kz

    service = client.get("/kz/almaty/remont-kvartir/").content.decode()
    assert "Как выбрать компанию" in service
    assert "Сравнительная таблица компаний" in service
    assert "Цены и смета" in service
    assert "Красные флаги" in service
    assert "Частые вопросы" in service

    ranking = client.get("/kz/almaty/reyting-remontnyh-kompaniy/").content.decode()
    assert "Как составлен рейтинг" in ranking
    assert "Сравнительная таблица рейтинга" in ranking
    assert "Жалобы и риски" in ranking
    assert "Ответ компании" in ranking

    dossier = client.get("/kz/company/alma-remont/").content.decode()
    assert "Короткий вывод" in dossier
    assert "Отзывы и рейтинг" in dossier
    assert "Жалобы и риски" in dossier
    assert "Внешняя проверка" in dossier
    assert "Официальный ответ компании" in dossier
    assert "Похожие компании" in dossier
    assert "Оставить отзыв" in dossier
    assert 'data-contact-placeholders="true"' in dossier
    assert "Контакты, адрес и карта" in dossier
    assert "Фото" in dossier
    assert "Карта" in dossier
    assert "Адрес не подтверждён" in dossier
    assert "Мы не подставляем выдуманный адрес" in dossier

    service = client.get("/kz/almaty/remont-kvartir/").content.decode()
    assert "Фото" in service
    assert "Адрес и карта — в досье после подтверждения источников" in service

    ranking = client.get("/kz/almaty/reyting-remontnyh-kompaniy/").content.decode()
    assert "Фото" in ranking
    assert "Адрес, карта и контакты показываются в досье" in ranking