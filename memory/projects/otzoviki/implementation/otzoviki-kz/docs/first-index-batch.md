# First index batch

This batch is the first controlled set of URLs allowed for Yandex Webmaster, Google Search Console and IndexNow submission after production smoke passes.

Rules:

- do not submit noindex pages;
- do not submit search, claim-profile, B2B forms, QR, admin, private workspace, or empty profiles;
- submit only pages that return 200 and `index,follow` on the production origin;
- run `python manage.py seed_launch_cut_content` and `python manage.py run_launch_cut_crawl` before exporting;
- use `/admin/launch-qa/first-index-batch.csv` as the staff-only export.

Manual systems:

- Yandex Webmaster: verify site, submit sitemap, then submit first batch if available.
- Google Search Console: verify property, submit sitemap, inspect first batch samples.
- IndexNow: verify key outside repo, submit first batch only after production smoke.
