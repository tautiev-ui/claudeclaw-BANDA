# Robots / Sitemap Validation Notes

Host: `https://otzoviki.kz`

Before manual submission:

1. Fetch `https://otzoviki.kz/robots.txt` from production.
2. Fetch `https://otzoviki.kz/sitemap.xml` from production.
3. Confirm every URL in `yandex_webmaster_first_batch.txt` returns `200` and `<meta name="robots" content="index,follow">`.
4. Confirm no `/search/`, `/claim-profile/`, `/admin/`, private workspace, QR redirect, or noindex pages are present.
5. Submit manually in Yandex Webmaster / Google Search Console / IndexNow only after production smoke passes.
