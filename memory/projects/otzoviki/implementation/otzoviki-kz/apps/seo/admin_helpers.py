from django.utils import timezone


def indexability_badge(obj) -> str:
    decision = obj.get_indexability_decision(require_trust_data=True)
    return f"✅ {decision.reason}" if decision.allowed else f"🚫 {decision.reason}"


def freshness_badge(obj, *, max_age_days: int = 90) -> str:
    last_verified_at = getattr(obj, "last_verified_at", None)
    if not last_verified_at:
        return "🚫 never verified"
    if last_verified_at < timezone.now() - timezone.timedelta(days=max_age_days):
        return "⚠️ stale"
    return "✅ fresh"


def required_trust_fields_missing(obj) -> list[str]:
    missing: list[str] = []
    if not getattr(obj, "source_count", 0):
        missing.append("source_count")
    if not getattr(obj, "last_verified_at", None):
        missing.append("last_verified_at")
    if not getattr(obj, "methodology_version", ""):
        missing.append("methodology_version")
    return missing
