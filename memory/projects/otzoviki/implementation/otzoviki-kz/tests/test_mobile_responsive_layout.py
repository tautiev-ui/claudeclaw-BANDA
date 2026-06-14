from pathlib import Path

import pytest
from django.test import Client


CSS_PATH = Path(__file__).resolve().parents[1] / "static" / "css" / "otzoviki-design-system.css"


def css_text():
    return CSS_PATH.read_text(encoding="utf-8")


@pytest.mark.django_db
def test_mobile_header_uses_link_chips_not_details():
    response = Client().get("/")
    assert response.status_code == 200
    html = response.content.decode()
    assert '<nav class="otz-city-selector"' in html
    assert "<details" not in html
    assert "<summary" not in html
    assert 'class="otz-city-choice"' in html


def test_mobile_search_input_is_visible_and_button_scoped():
    css = css_text()
    assert ".otz-search-form { flex-direction: column" in css
    assert ".otz-search-input" in css
    assert "min-height: 48px" in css
    assert "-webkit-appearance: none" in css
    assert ".otz-search-form .otz-btn { width: 100%" in css
    assert ".otz-btn { width: 100%; }" not in css


def test_mobile_header_has_safe_area_and_no_horizontal_overflow_rules():
    css = css_text()
    assert "env(safe-area-inset-left)" in css
    assert "overflow-x: hidden" in css
    assert ".otz-site-header { min-height: var(--header-mobile-height); }" in css
    assert ".otz-city-selector" in css
    assert "overflow-x: auto" in css
    assert "-webkit-overflow-scrolling: touch" in css


def test_global_forms_are_mobile_width_safe():
    css = css_text()
    assert "form.otz-card input:not(.otz-search-input)" in css
    assert "max-width: 100%" in css
    assert "appearance: none" in css
