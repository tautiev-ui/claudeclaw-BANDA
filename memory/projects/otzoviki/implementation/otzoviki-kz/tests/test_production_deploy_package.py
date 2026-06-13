from pathlib import Path


def test_production_deploy_package_contains_secret_safe_service_templates():
    required = {
        "deploy/gunicorn/otzoviki.service.example": ["EnvironmentFile=/etc/otzoviki/otzoviki.env", "gunicorn config.wsgi:application", "DJANGO_SETTINGS_MODULE=config.settings.prod"],
        "deploy/nginx/otzoviki.conf.example": ["server_name", "proxy_pass http://127.0.0.1:8000", "location /static/"],
        "deploy/env/production.env.example": ["DJANGO_SECRET_KEY=<set-in-secret-manager>", "DATABASE_URL=postgres://<user>:<password>@<host>:5432/<database>", "DJANGO_DEBUG=false"],
        "docs/production-rollback-runbook.md": ["Rollback", "python manage.py migrate", "restore"],
    }
    for rel_path, markers in required.items():
        path = Path(rel_path)
        assert path.exists(), rel_path
        body = path.read_text()
        for marker in markers:
            assert marker in body
        assert "change-me" not in body
        assert "otzoviki:otzoviki" not in body
        assert "BEGIN PRIVATE KEY" not in body
