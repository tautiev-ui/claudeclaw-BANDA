import pytest
from django.utils import timezone

from apps.editorial.models import Author, EditorialPolicy, MethodologyVersion


@pytest.mark.django_db
def test_author_public_name_and_profile_url():
    author = Author.objects.create(
        full_name="Алексей Редактор",
        role=Author.Role.EDITOR,
        slug="aleksey-redaktor",
        bio="Редактор Otzoviki по ремонтным компаниям.",
        expertise="Отзывы, сметы, договоры, проверка подрядчиков",
        is_active=True,
    )

    assert str(author) == "Алексей Редактор"
    assert author.public_label == "Алексей Редактор — редактор"
    assert author.get_absolute_url() == "/about/authors/aleksey-redaktor/"


@pytest.mark.django_db
def test_methodology_version_current_manager_and_label():
    MethodologyVersion.objects.create(
        version="v0",
        title="Old methodology",
        summary="Old",
        is_current=False,
        published_at=timezone.now(),
    )
    current = MethodologyVersion.objects.create(
        version="v1",
        title="Otzoviki KZ rating methodology",
        summary="How ratings and trust signals are calculated.",
        is_current=True,
        published_at=timezone.now(),
    )

    assert MethodologyVersion.objects.current() == current
    assert current.public_label == "Методология v1"
    assert current.get_absolute_url() == "/methodology/"


@pytest.mark.django_db
def test_editorial_policy_path_and_public_label():
    policy = EditorialPolicy.objects.create(
        kind=EditorialPolicy.Kind.REVIEW_POLICY,
        title="Правила публикации отзывов",
        slug="review-policy",
        summary="Отзывы проходят модерацию и не удаляются за оплату.",
        body="Policy body",
        is_published=True,
        updated_at=timezone.now(),
    )

    assert str(policy) == "Правила публикации отзывов"
    assert policy.get_absolute_url() == "/review-policy/"
    assert policy.public_label == "Правила публикации отзывов · опубликовано"


@pytest.mark.django_db
def test_unpublished_editorial_policy_is_not_public():
    policy = EditorialPolicy.objects.create(
        kind=EditorialPolicy.Kind.METHODOLOGY,
        title="Draft methodology",
        slug="methodology-draft",
        summary="Draft",
        body="Draft body",
        is_published=False,
    )

    assert policy.public_label == "Draft methodology · черновик"
