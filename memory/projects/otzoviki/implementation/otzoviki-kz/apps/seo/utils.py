from urllib.parse import urlsplit


def normalize_canonical_path(path: str) -> str:
    """Return an SEO-safe canonical path with no query/fragment and trailing slash."""
    if not path:
        return "/"
    parsed = urlsplit(path)
    clean = parsed.path or "/"
    if not clean.startswith("/"):
        clean = f"/{clean}"
    if clean != "/" and not clean.endswith("/"):
        clean = f"{clean}/"
    return clean


def build_absolute_canonical_url(request, path: str) -> str:
    return request.build_absolute_uri(normalize_canonical_path(path))
