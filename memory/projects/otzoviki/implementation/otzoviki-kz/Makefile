PYTHON ?= python
PIP ?= python -m pip

.PHONY: install check test migrate seed-launch launch-crawl operator-readiness production-handoff markin-next-wave company-import-example company-import-dry-run company-publish-dry-run search-submission-package verify

install:
	$(PIP) install --upgrade pip
	$(PIP) install "Django>=5.0,<5.3" "psycopg[binary]>=3.2" "redis>=5" "meilisearch>=0.31" "django-environ>=0.11" "whitenoise>=6.7" "gunicorn>=22" "pytest>=8" "pytest-django>=4.8"

check:
	$(PYTHON) manage.py check

test:
	pytest -q

migrate:
	$(PYTHON) manage.py migrate

seed-launch:
	$(PYTHON) manage.py seed_launch_cut_content

launch-crawl:
	$(PYTHON) manage.py run_launch_cut_crawl

operator-readiness:
	$(PYTHON) manage.py prepare_launch_operator_readiness

production-handoff:
	$(PYTHON) manage.py prepare_production_launch_handoff

markin-next-wave:
	$(PYTHON) manage.py seed_markin_next_wave_page_maps

company-import-example:
	$(PYTHON) manage.py import_company_dossiers docs/company-import-template.csv --report docs/company-import-report.csv

company-import-dry-run:
	$(PYTHON) manage.py import_company_dossiers docs/company-import-template.csv --report docs/company-import-dry-run-report.csv --dry-run

company-publish-dry-run:
	$(PYTHON) manage.py publish_company_dossiers --report docs/company-publish-dry-run-report.csv --dry-run

search-submission-package:
	$(PYTHON) manage.py export_search_submission_package --output-dir docs/search-submission-package --host https://otzoviki.kz

verify: check test
