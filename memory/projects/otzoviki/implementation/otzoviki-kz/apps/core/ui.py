from __future__ import annotations

from decimal import Decimal
from typing import Iterable

from apps.companies.models import Company
from apps.evidence.models import ExternalSource
from apps.reviews.models import RatingSnapshot


SOURCE_LABELS = {
    ExternalSource.SourceType.YANDEX: "Яндекс",
    ExternalSource.SourceType.TWO_GIS: "2ГИС",
    ExternalSource.SourceType.GOOGLE: "Google",
    ExternalSource.SourceType.WEBSITE: "Сайт",
    ExternalSource.SourceType.OTHER: "Источник",
}


def _rating_float(value) -> float:
    if value in (None, ""):
        return 0.0
    if isinstance(value, Decimal):
        return float(value)
    return float(value)


def _stars(value) -> str:
    rating = _rating_float(value)
    full = max(0, min(5, int(round(rating))))
    return "★" * full + "☆" * (5 - full)


def _source_badges(source_rows: list[ExternalSource]) -> list[dict[str, str]]:
    seen = []
    for source in source_rows:
        label = SOURCE_LABELS.get(source.source_type, source.name or "Источник")
        if label not in seen:
            seen.append(label)
    return [{"label": label, "kind": "evidence"} for label in seen[:3]]


def _verified_badges(company: Company, source_rows: list[ExternalSource], snapshot: RatingSnapshot | None) -> list[dict[str, str]]:
    verified_count = sum(1 for source in source_rows if source.same_as_verified)
    badges: list[dict[str, str]] = []
    if verified_count >= 2:
        badges.append({"label": "Источники сверены", "kind": "verified"})
    elif verified_count == 1:
        badges.append({"label": "1 источник сверяется", "kind": "evidence"})
    else:
        badges.append({"label": "Нужна сверка источников", "kind": "warn"})

    if company.profile_status == Company.ProfileStatus.CLAIMED:
        badges.append({"label": "Профиль заявлен", "kind": "business"})
    elif company.profile_status == Company.ProfileStatus.VERIFIED:
        badges.append({"label": "Профиль подтверждён", "kind": "verified"})
    else:
        badges.append({"label": "Профиль не заявлен", "kind": "neutral"})

    if snapshot and snapshot.review_count >= 50 and _rating_float(snapshot.average_rating) >= 4.5:
        badges.append({"label": "Высокий рейтинг", "kind": "elite"})
    return badges


def _risk_badge(company: Company, source_rows: list[ExternalSource], snapshot: RatingSnapshot | None) -> dict[str, str]:
    verified_count = sum(1 for source in source_rows if source.same_as_verified)
    if verified_count >= 2 and snapshot and snapshot.review_count > 0:
        return {"label": "Проверить детали", "kind": "ok", "detail": "есть рейтинг и внешние источники"}
    if verified_count >= 2:
        return {"label": "Мало отзывов", "kind": "warn", "detail": "источники есть, рейтинг ещё слабый"}
    return {"label": "Нужна сверка", "kind": "risk", "detail": "откройте досье перед авансом"}


def _trust_percent(snapshot: RatingSnapshot | None) -> int | None:
    if not snapshot or snapshot.review_count <= 0:
        return None
    return max(0, min(100, round(_rating_float(snapshot.average_rating) / 5 * 100)))


def _public_description(company: Company) -> str:
    text = (company.short_description or "").strip()
    internal_markers = ["verified candidate", "source:", "http://", "https://", "тендер", "production", "sameAs"]
    if not text or any(marker.lower() in text.lower() for marker in internal_markers):
        return "Досье компании: отзывы, внешние источники, контакты и риски перед договором."
    return text


def build_company_cards(companies: Iterable[Company]) -> list[dict]:
    companies = list(companies)
    snapshots = {snapshot.company_id: snapshot for snapshot in RatingSnapshot.objects.filter(company__in=companies)}
    sources_by_company: dict[int, list[ExternalSource]] = {company.id: [] for company in companies}
    for source in ExternalSource.objects.filter(company__in=companies).order_by("company_id", "source_type", "name"):
        sources_by_company.setdefault(source.company_id, []).append(source)

    cards = []
    for company in companies:
        snapshot = snapshots.get(company.id)
        source_rows = sources_by_company.get(company.id, [])
        trust_percent = _trust_percent(snapshot)
        rating = _rating_float(snapshot.average_rating) if snapshot else 0.0
        cards.append(
            {
                "company": company,
                "snapshot": snapshot,
                "description": _public_description(company),
                "rating": rating,
                "stars": _stars(rating) if snapshot and snapshot.review_count > 0 else "☆☆☆☆☆",
                "trust_percent": trust_percent,
                "trust_bar_width": trust_percent or 0,
                "review_count": snapshot.review_count if snapshot else 0,
                "source_badges": _source_badges(source_rows),
                "verified_badges": _verified_badges(company, source_rows, snapshot),
                "verified_source_count": sum(1 for source in source_rows if source.same_as_verified),
                "risk_badge": _risk_badge(company, source_rows, snapshot),
                "response_label": "Ответ компании пока не зафиксирован",
                "contact_label": "Контакты сверяйте в досье" if not company.phone else "Телефон указан в досье",
            }
        )
    return cards
