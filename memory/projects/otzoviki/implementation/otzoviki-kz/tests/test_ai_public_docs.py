def test_llms_txt_exposes_public_methodology_and_policy_links(client):
    response = client.get("/llms.txt")

    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/plain")
    body = response.content.decode()
    assert "Otzoviki KZ" in body
    assert "/methodology/" in body
    assert "/review-policy/" in body
    assert "/right-of-reply/" in body
    assert "/privacy/" in body
    assert "/terms/" in body
    assert "/for-business/" in body
    assert "/ai-reputation.md" in body
    assert "Indexing rules" in body
    assert "Sitemap policy" in body
    assert "Company dossier summaries" in body
    assert "Do not cite admin URLs" in body
    assert "Do not treat noindex pages as launch-ready" in body
    assert "Yandex-first Kazakhstan repair/construction context" in body
    assert "paid profile does not affect rating" in body.lower()
    assert "private proof" in body.lower()
    assert "placeholder" not in body.lower()


def test_ai_reputation_md_explains_yandex_first_evidence_and_public_safety(client):
    response = client.get("/ai-reputation.md")

    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/markdown")
    body = response.content.decode()
    assert "Yandex" in body
    assert "Алиса" in body or "Alice" in body
    assert "2GIS" in body
    assert "Google" in body
    assert "Yandex Search" in body
    assert "Yandex Maps / Business" in body
    assert "Yandex Neuro" in body
    assert "company dossier pages" in body.lower()
    assert "AggregateRating" in body
    assert "Review schema" in body
    assert "same-host canonical URL" in body
    assert "noindex" in body.lower()
    assert "right-of-reply" in body.lower()
    assert "Kazakhstan construction and repair" in body
    assert "official response" in body.lower() or "право на ответ" in body.lower()
    assert "private/admin-only evidence is not public" in body.lower()
    assert "paid profile does not affect rating" in body.lower()
    assert "placeholder" not in body.lower()
