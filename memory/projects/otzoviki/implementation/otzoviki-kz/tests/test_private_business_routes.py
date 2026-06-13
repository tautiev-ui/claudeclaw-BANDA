import pytest
from django.contrib.auth import get_user_model


@pytest.mark.django_db
def test_private_business_route_redirects_anonymous_users_to_login(client):
    response = client.get("/business/dashboard/")

    assert response.status_code == 302
    assert "/admin/login/" in response["Location"]


@pytest.mark.django_db
def test_private_business_route_is_noindex_for_authenticated_staff(client):
    user = get_user_model().objects.create_user(username="owner", password="pass", is_staff=True)
    client.force_login(user)

    response = client.get("/business/dashboard/")

    assert response.status_code == 200
    html = response.content.decode()
    assert '<meta name="robots" content="noindex,follow">' in html
    assert '<link rel="canonical" href="http://testserver/business/dashboard/">' in html
    assert "Business dashboard" in html
    assert "Private workspace" in html
