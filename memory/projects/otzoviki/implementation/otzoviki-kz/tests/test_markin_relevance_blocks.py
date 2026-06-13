import csv
import io

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command

from apps.keywords.models import KeywordPageMap


@pytest.mark.django_db
def test_markin_relevance_blocks_export_requires_staff_and_maps_page_type_actions(client):
    response = client.get("/admin/keywords/markin-relevance-blocks.csv")
    assert response.status_code == 302
    assert "/admin/login/" in response["Location"]

    call_command("seed_markin_next_wave_page_maps")
    staff = get_user_model().objects.create_user(username="markin-relevance", password="pass", is_staff=True)
    client.force_login(staff)

    response = client.get("/admin/keywords/markin-relevance-blocks.csv")

    assert response.status_code == 200
    assert response["Content-Type"] == "text/csv; charset=utf-8"
    assert response["Content-Disposition"] == 'attachment; filename="markin-relevance-blocks.csv"'
    rows = list(csv.DictReader(io.StringIO(response.content.decode())))
    assert rows
    assert {"page_type", "block_key", "required", "indexability_gate", "template_hint", "markin_reason"}.issubset(rows[0].keys())
    by_type = {}
    for row in rows:
        by_type.setdefault(row["page_type"], set()).add(row["block_key"])
    assert {"local_proof", "company_list", "faq", "internal_links"}.issubset(by_type[KeywordPageMap.PageType.CITY_SERVICE])
    assert {"methodology", "comparison_table", "rating_disclosure", "company_list"}.issubset(by_type[KeywordPageMap.PageType.RANKING])
    assert {"price_ranges", "smeta_checklist", "risk_disclaimer", "company_links"}.issubset(by_type[KeywordPageMap.PageType.PRICE])
    assert {"external_sources", "right_of_reply", "trust_summary", "review_cta"}.issubset(by_type[KeywordPageMap.PageType.COMPANY_DOSSIER])
    assert {"sources", "checklist", "risk_mitigation", "money_links"}.issubset(by_type[KeywordPageMap.PageType.GUIDE])
    assert all(row["required"] == "true" for row in rows)
    assert any(row["indexability_gate"] == "block_index_until_present" for row in rows)
