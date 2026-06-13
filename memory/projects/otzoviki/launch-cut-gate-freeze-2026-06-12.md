# Otzoviki KZ — Launch-cut gate freeze

Date: 2026-06-12
Current implementation baseline: OTZ-1822 completed.
Mode requested by user: 300 gates per batch.
Scope of this freeze: MVP launch-cut only, not MVP-2 growth/boosters and not actual external submissions/deployments.

## Verification baseline used

Live/project checks performed from `/root/claudeclaw-BANDA/memory/projects/otzoviki/implementation/otzoviki-kz`:

- `python manage.py check` => no issues.
- `pytest -q` => 204 passed.
- Test files: 65.
- App migrations: 25.
- Management commands found:
  - `apps/keywords/management/commands/import_stage4a_keywords.py`
  - `apps/services/management/commands/seed_markin_services.py`
- Current URL surface includes public routes, private B2B routes, launch QA dashboards, route-smoke exports/live, deployment machine bundle, and submission machine bundle.

## Current data/content probes

Live route probe summary:

- `/` => 200, index,follow
- `/kz/` => 200, index,follow
- `/kz/almaty/` => 200, index,follow
- `/kz/astana/` => 200, noindex,follow
- `/kz/almaty/remont-kvartir/` => 200, index,follow
- `/kz/astana/remont-kvartir/` => 200, noindex,follow
- `/kz/almaty/reyting-remontnyh-kompaniy/` => 200, index,follow
- `/kz/almaty/remont-kvartir/ceny/` => 200, index,follow
- `/kz/guides/` => 200, index,follow
- policy/B2B/SEO docs routes render as expected; forms/search are noindex where expected.

Database/content counts from current dev DB:

- companies: 2
- indexable companies: 0
- guides: 1
- launch-ready guides: 0
- cities: 1
- services: 7
- keywords: 24,800
- keyword evidence rows: 9,246
- clusters: 7
- page maps: 7
- analytics events: 8
- QR flows: 1
- platform links: 1
- methodologies: 0
- editorial policies: 0
- authors: 0
- editors: 0
- reviewers: 0
- launch checks: 7
- indexing monitor rows: 0
- webmaster tasks: 8

## Stage 10 launch-cut interpretation

Already substantially implemented as code/guardrails:

- Django SSR scaffold/apps/routes.
- Public SEO routes/templates and noindex/canonical basics.
- Stage 4A keyword import exists and imported data is present.
- Review, B2B, moderation, audit logs, claim/official response/reputation audit flows.
- QR baseline.
- SEO machine docs: robots/sitemap/llms/ai-reputation.
- Launch QA machine surfaces: route smoke, blockers, release readiness, deployment handoff, submission package.

Not launch-ready yet because launch-cut requires filled content/data and final verification artifacts:

- 50–100 filled company dossiers; current DB has 2 companies and 0 indexable companies.
- Almaty/Astana launch depth; current DB has only 1 city, and Astana routes are noindex.
- 4 P0 guides launch-ready; current DB has 1 guide and 0 launch-ready guides.
- Methodology/editorial policy/authors/editors/reviewers seeded; current DB has 0.
- Final schema validation/crawl/E-E-A-T launch report not yet frozen as artifact.
- Webmaster verification/analytics staging toggles and evidence not fully frozen.
- CDN/origin/bot QA/fallback docs and final launch handoff docs not yet frozen.
- Manual external submissions must remain outside automation; current submission package is ready as a non-mutating operator artifact, but evidence of actual manual submission is not in scope until production/staging access exists.

## Remaining gates to MVP launch-cut

Final frozen remaining count: **2,100 gates**.

That is exactly **7 batches × 300 gates** from current OTZ-1822 baseline.

### OTZ-1823..2122 — Submission evidence package

Purpose: staff-only evidence log/checklist for actual manual post-deploy submission steps without performing external submissions.

Scope:

- Submission evidence JSON/CSV/LIVE or dashboard layer.
- Manual evidence fields for Yandex/GSC/IndexNow/sitemap/AI docs.
- Proof placeholders, timestamps, operator, target, status, source path, risk state.
- Links from existing submission/deployment/ops surfaces.
- No credentials, no external network, no mutation of production state.

### OTZ-2123..2422 — Editorial/E-E-A-T seed foundation

Purpose: seed and verify MethodologyVersion, EditorialPolicy pages, Author/editor/reviewer roles, and trust metadata.

Scope:

- Methodology/current version seed.
- Review policy, right-of-reply, privacy, terms/editorial policy content source.
- Author/editor/reviewer records.
- Trust strip consistency.
- E-E-A-T gate visibility on public page types.
- Admin/report checks for missing editorial trust fields.

### OTZ-2423..2722 — Launch data seed and completeness report

Purpose: satisfy launch-cut data minimum for Almaty/Astana and company dossiers.

Scope:

- Seed/import format for 50–100 companies.
- City/service/company coverage for Almaty + Astana.
- ExternalSource/sameAs footprints where verified.
- Company completeness and indexability report.
- No empty profile becomes indexable.
- Astana routes move from noindex only when data depth is present.

### OTZ-2723..3022 — P0 guide content batch

Purpose: seed 4 launch-ready P0 guides and verify guide quality gates.

Scope:

- 4 P0 guides from Stage 10 launch cut.
- Author/editor/updated_at/sources/checklist/risk/FAQ/internal links.
- Guide hub quality and noindex/index transitions.
- FAQPage/Article gating against visible content.
- Money-page internal link coverage.

### OTZ-3023..3322 — Schema/crawl/E-E-A-T validation package

Purpose: final crawl-style QA artifact before first index batch.

Scope:

- Internal crawl report over launch-cut routes.
- Canonical/noindex/schema validation result rows.
- AggregateRating/Review/FAQ/sameAs restrictions verified on seeded data.
- Empty/thin page suppression checked.
- Launch blocker integration from crawl results.

### OTZ-3323..3622 — Analytics + Webmaster verification readiness

Purpose: finish measurable operating loop without requiring production credentials in code.

Scope:

- Analytics config flags and disabled-in-test/dev safety.
- Event coverage for search, dossier open, review submit, claim, audit, guide CTA, QR click.
- Webmaster/GSC/Yandex verification tag/file support via config placeholders.
- Staff report showing readiness/missing config.
- Staging-safe evidence artifacts.

### OTZ-3623..3922 — CDN/origin/bot QA + final launch report

Purpose: final manual launch handoff before index release.

Scope:

- Conservative Cloudflare settings documentation.
- DNS-only fallback procedure.
- Bunny CDN secondary fallback note.
- Direct-origin public crawl/bot-like QA plan.
- Googlebot/YandexBot-like fetch checks.
- Final launch QA report combining data completeness, crawl/schema/E-E-A-T, analytics/webmaster, submission package readiness.

## Count summary

- Completed through at freeze creation: OTZ-1822.
- Frozen remaining at freeze creation: 2,100 gates.
- Frozen 300-gate batches at freeze creation: 7.
- Final launch-cut target after freeze: OTZ-3922.
- Current implementation status after execution on 2026-06-12: completed through OTZ-3922; remaining frozen launch-cut gates: 0.
- Excluded from this count: MVP-2 growth/boosters, real production deploy, real external Yandex/GSC/IndexNow submissions, paid/external actions, and broader GEO/AEO expansion after MVP launch.
