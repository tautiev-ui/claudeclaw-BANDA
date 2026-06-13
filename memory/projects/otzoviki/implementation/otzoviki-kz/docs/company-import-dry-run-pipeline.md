# Company import dry-run pipeline

Операторский пайплайн для первого real-company импорта в Otzoviki KZ. Цель: принять CSV компаний Алматы, проверить дубли/обязательные поля, получить отчёт, затем импортировать только как `draft/noindex`. Публикация в индекс идёт отдельным trust gate.

## Входной CSV

Базовый шаблон: `docs/company-import-template.csv`.

Рабочий пример для проверки пайплайна: `docs/company-import-real-companies-sample.csv`.

Обязательные заголовки:

```csv
name,city_slug,service_slug,website_url,phone,yandex_url,two_gis_url,short_description
```

Правила заполнения:

- `city_slug`: для первой партии `almaty`.
- `service_slug`: для первой партии `remont-kvartir`.
- `website_url`, `yandex_url`, `two_gis_url`: нормализуются, используются для duplicate checks.
- `short_description`: нейтральное описание без рекламных обещаний и без копирования чужих отзывов.
- Внешние площадки — только evidence/footprint, не источник AggregateRating.

## Dry-run перед импортом

Сначала применить миграции на локальной/стейджинговой БД:

```bash
python manage.py migrate --noinput
python manage.py import_company_dossiers docs/company-import-real-companies-sample.csv --dry-run --report docs/company-import-dry-run-report.csv
```

Ожидаемый результат:

- DB не мутируется.
- В report строки получают `status=dry_run`, `reason=would_create_draft_noindex`.
- Дубли получают `status=duplicate` и причину `duplicate_website_url`, `duplicate_yandex_url` или `duplicate_2gis_url`.

## Safe import после проверки отчёта

Запускать только если dry-run report чистый и вручную проверены источники:

```bash
python manage.py import_company_dossiers docs/company-import-real-companies-sample.csv --report docs/company-import-report.csv
```

Результат импорта:

- создаются Company как `draft/noindex`;
- создаётся city/service link;
- Yandex и 2GIS сохраняются как unverified ExternalSource;
- `source_count=0`, `last_verified_at=None`, `methodology_version=""`.

## Publish gate dry-run

Перед любой индексацией:

```bash
python manage.py publish_company_dossiers --dry-run --report docs/company-publish-dry-run-report.csv
```

Не запускать publish без проверки report. Компания может стать indexable только если проходит trust gate:

- активна;
- есть short description;
- заполнены SEO title/description/canonical;
- есть city/service link;
- есть минимум 2 verified external sources;
- после публикации ставится methodology version `company-dossier-trust-gate-v1`.

## Запрещено на первом импорте

- Не включать `indexable` вручную.
- Не копировать тексты отзывов из Яндекс/2GIS/Google.
- Не ставить verified sources без ручной проверки.
- Не запускать publish без проверки report.
- Не делать внешнюю отправку в Yandex/GSC/IndexNow из этого пайплайна.

## Recommended first batch

1. Собрать 20–50 компаний Алматы по `remont-kvartir`.
2. Заполнить CSV по шаблону.
3. Выполнить dry-run.
4. Исправить дубли и пустые поля.
5. Импортировать как `draft/noindex`.
6. Отдельно верифицировать источники и только затем запускать publish dry-run.
