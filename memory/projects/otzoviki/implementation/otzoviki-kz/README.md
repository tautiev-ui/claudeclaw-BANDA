# Otzoviki KZ MVP

SEO-first Django SSR scaffold for Otzoviki KZ.

## Local dev

```bash
cp .env.example .env
source .venv/bin/activate
python manage.py check
python manage.py runserver 0.0.0.0:8000
```

Health: `/health/`

## Stack

Django SSR + PostgreSQL + Redis + Meilisearch + Tailwind/HTMX-ready design CSS.
