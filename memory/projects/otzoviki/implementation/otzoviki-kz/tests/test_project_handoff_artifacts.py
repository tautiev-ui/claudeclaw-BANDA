from pathlib import Path


def test_ci_review_guide_and_makefile_are_present_and_secret_safe():
    root = Path(__file__).resolve().parents[6]
    project = Path(__file__).resolve().parents[1]
    files = {
        root / ".github/workflows/otzoviki-kz.yml": ["pytest -q", "python manage.py check", "pull_request"],
        project / "docs/PR_REVIEW_GUIDE.md": ["Suggested review order", "PR split plan", "Markin execution layer"],
        project / "Makefile": ["seed-launch", "launch-crawl", "markin-next-wave", "company-import-example"],
    }
    for path, markers in files.items():
        assert path.exists(), path
        body = path.read_text()
        for marker in markers:
            assert marker in body
        assert "github_pat_" not in body
        assert "BEGIN PRIVATE KEY" not in body
        assert "otzoviki:otzoviki" not in body
