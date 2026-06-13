from django.db import models


class Author(models.Model):
    class Role(models.TextChoices):
        AUTHOR = "author", "автор"
        EDITOR = "editor", "редактор"
        REVIEWER = "reviewer", "эксперт-рецензент"

    full_name = models.CharField(max_length=160)
    role = models.CharField(max_length=24, choices=Role.choices, default=Role.AUTHOR)
    slug = models.SlugField(max_length=180, unique=True)
    bio = models.TextField(blank=True)
    expertise = models.TextField(blank=True)
    same_as_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name

    @property
    def public_label(self) -> str:
        return f"{self.full_name} — {self.get_role_display()}"

    def get_absolute_url(self) -> str:
        return f"/about/authors/{self.slug}/"


class MethodologyVersionQuerySet(models.QuerySet):
    def current(self):
        return self.filter(is_current=True).order_by("-published_at", "-created_at").first()


class MethodologyVersion(models.Model):
    version = models.CharField(max_length=32, unique=True)
    title = models.CharField(max_length=255)
    summary = models.TextField()
    body = models.TextField(blank=True)
    is_current = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = MethodologyVersionQuerySet.as_manager()

    class Meta:
        ordering = ["-published_at", "-created_at"]

    def __str__(self):
        return f"{self.version} — {self.title}"

    @property
    def public_label(self) -> str:
        return f"Методология {self.version}"

    def get_absolute_url(self) -> str:
        return "/methodology/"


class EditorialPolicy(models.Model):
    class Kind(models.TextChoices):
        METHODOLOGY = "methodology", "Методология"
        REVIEW_POLICY = "review_policy", "Правила отзывов"
        RIGHT_OF_REPLY = "right_of_reply", "Право на ответ"
        PRIVACY = "privacy", "Privacy"
        TERMS = "terms", "Terms"

    kind = models.CharField(max_length=32, choices=Kind.choices)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=180, unique=True)
    summary = models.TextField(blank=True)
    body = models.TextField()
    is_published = models.BooleanField(default=False)
    updated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["kind", "title"]
        verbose_name_plural = "editorial policies"

    def __str__(self):
        return self.title

    @property
    def public_label(self) -> str:
        status = "опубликовано" if self.is_published else "черновик"
        return f"{self.title} · {status}"

    def get_absolute_url(self) -> str:
        routes = {
            self.Kind.METHODOLOGY: "/methodology/",
            self.Kind.REVIEW_POLICY: "/review-policy/",
            self.Kind.RIGHT_OF_REPLY: "/right-of-reply/",
            self.Kind.PRIVACY: "/privacy/",
            self.Kind.TERMS: "/terms/",
        }
        return routes.get(self.kind, f"/{self.slug}/")
