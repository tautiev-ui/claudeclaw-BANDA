from django.db import models


class WebmasterSetupTask(models.Model):
    class Platform(models.TextChoices):
        YANDEX = "yandex", "Yandex Webmaster"
        GOOGLE = "google", "Google Search Console"

    class Status(models.TextChoices):
        TODO = "todo", "To do"
        IN_PROGRESS = "in_progress", "In progress"
        DONE = "done", "Done"
        BLOCKED = "blocked", "Blocked"

    platform = models.CharField(max_length=24, choices=Platform.choices, db_index=True)
    task_key = models.SlugField(max_length=80)
    title = models.CharField(max_length=220)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.TODO, db_index=True)
    verification_url = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["platform", "task_key"]
        constraints = [models.UniqueConstraint(fields=["platform", "task_key"], name="unique_webmaster_setup_task")]
        indexes = [models.Index(fields=["platform", "status"])]

    @property
    def is_done(self) -> bool:
        return self.status == self.Status.DONE

    def __str__(self):
        return f"{self.get_platform_display()} · {self.title}"


DEFAULT_WEBMASTER_TASKS = [
    (WebmasterSetupTask.Platform.YANDEX, "verify-site", "Добавить и подтвердить сайт", "Подтвердить домен Otzoviki.kz в Yandex Webmaster без публикации секретов в репозитории."),
    (WebmasterSetupTask.Platform.YANDEX, "submit-sitemap", "Отправить sitemap.xml", "Отправить только индексируемые canonical URL; пустые, QR, поиск и private routes не должны попасть в sitemap."),
    (WebmasterSetupTask.Platform.YANDEX, "check-robots", "Проверить robots.txt", "Проверить, что robots разрешает public SEO pages и закрывает admin/search/private/campaign routes."),
    (WebmasterSetupTask.Platform.YANDEX, "monitor-indexing", "Включить мониторинг индексации", "Отслеживать submitted/indexed/noindex/empty profile states по MVP страницам."),
    (WebmasterSetupTask.Platform.GOOGLE, "verify-site", "Добавить и подтвердить сайт", "Подтвердить домен в Google Search Console через безопасный verification meta/env flow."),
    (WebmasterSetupTask.Platform.GOOGLE, "submit-sitemap", "Отправить sitemap.xml", "Сверить sitemap с public indexability gates перед отправкой."),
    (WebmasterSetupTask.Platform.GOOGLE, "check-robots", "Проверить robots.txt", "Проверить доступность public canonical routes и отсутствие indexing ловушек."),
    (WebmasterSetupTask.Platform.GOOGLE, "monitor-cwv", "Зафиксировать CWV/mobile baseline", "Проверить mobile usability и Core Web Vitals basics перед launch cut line."),
]


def ensure_default_webmaster_tasks() -> None:
    for platform, task_key, title, description in DEFAULT_WEBMASTER_TASKS:
        WebmasterSetupTask.objects.get_or_create(
            platform=platform,
            task_key=task_key,
            defaults={"title": title, "description": description},
        )


class LaunchQACheck(models.Model):
    class Category(models.TextChoices):
        ROUTES = "routes", "Routes and status codes"
        INDEXABILITY = "indexability", "Canonicals and robots meta"
        SCHEMA = "schema", "Schema matches visible content"
        SITEMAP_ROBOTS = "sitemap_robots", "Sitemap and robots.txt"
        MOBILE_CWV = "mobile_cwv", "Mobile and CWV basics"
        CONTENT = "content", "Content quality"

    class Status(models.TextChoices):
        TODO = "todo", "To do"
        PASSED = "passed", "Passed"
        FAILED = "failed", "Failed"
        BLOCKED = "blocked", "Blocked"

    category = models.CharField(max_length=32, choices=Category.choices, db_index=True)
    check_key = models.SlugField(max_length=100)
    title = models.CharField(max_length=240)
    target = models.CharField(max_length=300, blank=True)
    expected = models.TextField(blank=True)
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.TODO, db_index=True)
    evidence = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["category", "check_key"]
        constraints = [models.UniqueConstraint(fields=["category", "check_key"], name="unique_launch_qa_check")]
        indexes = [models.Index(fields=["category", "status"])]

    @property
    def is_done(self) -> bool:
        return self.status == self.Status.PASSED

    def __str__(self):
        return f"{self.get_category_display()} · {self.title}"


DEFAULT_LAUNCH_QA_CHECKS = [
    (LaunchQACheck.Category.ROUTES, "public-routes-200", "Routes and status codes", "/, /kz/, /kz/{city}/, company, guides, B2B", "Public MVP routes return expected 200/404/302 codes."),
    (LaunchQACheck.Category.INDEXABILITY, "canonical-robots", "Canonicals and robots meta", "public and empty-state pages", "Indexable pages have canonical + index,follow; search/forms/QR/private/empty states stay noindex,follow."),
    (LaunchQACheck.Category.SCHEMA, "visible-content-schema", "Schema matches visible content", "JSON-LD blocks", "Review/AggregateRating/FAQ/Breadcrumb/ItemList schema must reflect visible public content only."),
    (LaunchQACheck.Category.SITEMAP_ROBOTS, "sitemap-indexable-only", "Sitemap only contains indexable canonical URLs", "/sitemap.xml", "Exclude noindex, QR, search, private, admin and empty profiles."),
    (LaunchQACheck.Category.SITEMAP_ROBOTS, "robots-rules", "Robots public/private rules", "/robots.txt", "Allow public SEO pages and disallow admin/search/private/campaign-style routes."),
    (LaunchQACheck.Category.MOBILE_CWV, "mobile-cwv-baseline", "Mobile and CWV basics", "public templates", "Check responsive layout, header/search usability, CSS/static delivery and Core Web Vitals baseline."),
    (LaunchQACheck.Category.CONTENT, "guides-quality", "Guides are sourced and not orphan generic filler", "/kz/guides/", "Published guides have sources, checklist/risk/FAQ blocks and links to money pages."),
]


def ensure_default_launch_qa_checks() -> None:
    for category, check_key, title, target, expected in DEFAULT_LAUNCH_QA_CHECKS:
        LaunchQACheck.objects.get_or_create(
            category=category,
            check_key=check_key,
            defaults={"title": title, "target": target, "expected": expected},
        )


class IndexingMonitorURL(models.Model):
    class IndexStatus(models.TextChoices):
        DISCOVERED = "discovered", "Discovered"
        SUBMITTED = "submitted", "Submitted"
        INDEXED = "indexed", "Indexed"
        NOINDEX = "noindex", "Noindex"
        EXCLUDED = "excluded", "Excluded"
        ERROR = "error", "Error"

    url = models.CharField(max_length=500, unique=True)
    page_type = models.CharField(max_length=80, db_index=True)
    index_status = models.CharField(max_length=32, choices=IndexStatus.choices, default=IndexStatus.DISCOVERED, db_index=True)
    http_status = models.PositiveSmallIntegerField(null=True, blank=True)
    is_empty_profile = models.BooleanField(default=False, db_index=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    indexed_at = models.DateTimeField(null=True, blank=True)
    last_checked_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["page_type", "url"]
        indexes = [models.Index(fields=["index_status", "is_empty_profile"])]

    @property
    def has_launch_risk(self) -> bool:
        risky_status = self.index_status in {self.IndexStatus.SUBMITTED, self.IndexStatus.INDEXED}
        has_http_error = self.http_status is not None and self.http_status >= 400
        return risky_status and (self.is_empty_profile or has_http_error)

    def __str__(self):
        return f"{self.url} · {self.get_index_status_display()}"
