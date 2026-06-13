# Production Rollback Runbook

Manual-safe rollback notes for Otzoviki KZ. Store no secrets in this file.

## Before rollback

1. Record current release SHA and timestamp.
2. Save application logs and `python manage.py check` output.
3. Confirm whether rollback needs code only, database restore, or both.

## Code rollback

```bash
cd /srv/otzoviki/current
git fetch --all
git checkout <previous-good-sha>
. .venv/bin/activate
python manage.py collectstatic --noinput
python manage.py check
sudo systemctl restart otzoviki
```

## Database migration rollback

Only run migration rollback if the release introduced migrations and the rollback plan is verified:

```bash
. .venv/bin/activate
python manage.py showmigrations
python manage.py migrate <app_label> <previous_migration>
python manage.py check
```

## Restore from backup

If data integrity is affected, stop writes, restore the latest verified backup, run `python manage.py migrate`, then run launch smoke checks.

## Post-rollback smoke

- `/health/` returns 200.
- Public launch pages return 200.
- Admin launch QA endpoints require login.
- `python manage.py run_launch_cut_crawl` has zero errors.
