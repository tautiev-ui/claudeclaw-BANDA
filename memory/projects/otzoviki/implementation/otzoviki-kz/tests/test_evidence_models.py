import pytest
from django.utils import timezone

from apps.companies.models import Company
from apps.evidence.models import Evidence, ExternalSource


@pytest.mark.django_db
def test_external_source_same_as_label_and_str():
    company = Company.objects.create(name="Alma Remont", slug="alma-remont")
    source = ExternalSource.objects.create(
        company=company,
        source_type=ExternalSource.SourceType.YANDEX,
        name="Яндекс Бизнес",
        url="https://yandex.kz/maps/org/alma-remont/",
        same_as_verified=True,
        captured_at=timezone.now(),
    )

    assert str(source) == "Alma Remont · Яндекс Бизнес"
    assert source.public_label == "Яндекс Бизнес · sameAs verified"


@pytest.mark.django_db
def test_public_evidence_excludes_private_proof():
    company = Company.objects.create(name="Alma Remont", slug="alma-remont")
    public = Evidence.objects.create(
        company=company,
        evidence_type=Evidence.EvidenceType.EXTERNAL_FOOTPRINT,
        title="Яндекс профиль найден",
        claim="Компания присутствует в Яндекс Картах",
        source_url="https://yandex.kz/maps/org/alma-remont/",
        visibility=Evidence.Visibility.PUBLIC,
        captured_at=timezone.now(),
    )
    private_proof = Evidence.objects.create(
        company=company,
        evidence_type=Evidence.EvidenceType.PRIVATE_PROOF,
        title="Чек клиента",
        claim="Private proof",
        visibility=Evidence.Visibility.PUBLIC,
        captured_at=timezone.now(),
    )

    assert list(Evidence.objects.public()) == [public]
    assert public.is_public is True
    assert private_proof.is_public is False
    assert public.public_label == "external_footprint · Яндекс профиль найден"


@pytest.mark.django_db
def test_evidence_without_source_url_can_be_editorial_note():
    company = Company.objects.create(name="Alma Remont", slug="alma-remont")
    evidence = Evidence.objects.create(
        company=company,
        evidence_type=Evidence.EvidenceType.EDITORIAL_NOTE,
        title="Редакционная проверка",
        claim="Данные проверены редактором",
        visibility=Evidence.Visibility.PUBLIC,
        captured_at=timezone.now(),
    )

    assert str(evidence) == "Alma Remont · Редакционная проверка"
    assert evidence.is_public is True
