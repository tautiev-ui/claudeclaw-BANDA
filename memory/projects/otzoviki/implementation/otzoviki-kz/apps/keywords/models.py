from django.db import models


class Keyword(models.Model):
    class Source(models.TextChoices):
        KEYS_SO = "keys_so", "Keys.so"
        MANUAL = "manual", "Manual"
        OTHER = "other", "Other"

    query = models.CharField(max_length=500)
    normalized_query = models.CharField(max_length=500, db_index=True, blank=True)
    frequency = models.PositiveIntegerField(default=0)
    source = models.CharField(max_length=32, choices=Source.choices, default=Source.KEYS_SO)
    region = models.CharField(max_length=32, blank=True)
    target_cluster = models.CharField(max_length=180, blank=True, db_index=True)
    collected_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-frequency", "normalized_query"]
        indexes = [models.Index(fields=["source", "region"])]

    def save(self, *args, **kwargs):
        self.normalized_query = " ".join(self.query.strip().lower().split())
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.normalized_query} · {self.frequency}"


class KeywordURLCompetitorEvidence(models.Model):
    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE, related_name="competitor_evidence")
    url = models.URLField(max_length=1000)
    domain = models.CharField(max_length=255, db_index=True)
    title = models.CharField(max_length=500, blank=True)
    h1 = models.CharField(max_length=500, blank=True)
    position = models.PositiveSmallIntegerField(null=True, blank=True)
    collected_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["keyword__normalized_query", "position", "domain"]
        indexes = [models.Index(fields=["domain", "position"])]

    def __str__(self):
        position = f"#{self.position}" if self.position else "no position"
        return f"{self.keyword.normalized_query} → {self.domain} · {position}"

    @property
    def is_top_10(self) -> bool:
        return self.position is not None and self.position <= 10


class KeywordCluster(models.Model):
    class Intent(models.TextChoices):
        COMMERCIAL = "commercial", "Commercial"
        NAVIGATIONAL = "navigational", "Navigational"
        INFORMATIONAL = "informational", "Informational"
        MIXED = "mixed", "Mixed"

    slug = models.SlugField(max_length=180, unique=True)
    name = models.CharField(max_length=240)
    intent = models.CharField(max_length=32, choices=Intent.choices, default=Intent.MIXED)
    page_type = models.CharField(max_length=48, blank=True)
    keywords = models.ManyToManyField(Keyword, related_name="clusters", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["slug"]

    def __str__(self):
        return self.name


class KeywordPageMap(models.Model):
    class PageType(models.TextChoices):
        COMPANY_DOSSIER = "company_dossier", "Company dossier"
        CITY_SERVICE = "city_service", "City service"
        RANKING = "ranking", "Ranking"
        PRICE = "price", "Price"
        CITY_HUB = "city_hub", "City hub"
        GUIDE = "guide", "Guide"
        OTHER = "other", "Other"

    class Priority(models.TextChoices):
        P0 = "P0", "P0"
        P1 = "P1", "P1"
        P2 = "P2", "P2"
        LATER = "later", "Later"

    MONEY_PAGE_TYPES = {PageType.COMPANY_DOSSIER, PageType.CITY_SERVICE, PageType.RANKING, PageType.PRICE, PageType.CITY_HUB}

    cluster = models.ForeignKey(KeywordCluster, on_delete=models.CASCADE, related_name="page_maps")
    page_type = models.CharField(max_length=48, choices=PageType.choices)
    canonical_pattern = models.CharField(max_length=300)
    priority = models.CharField(max_length=16, choices=Priority.choices, default=Priority.P1)
    is_indexable_candidate = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["priority", "page_type", "cluster__slug"]
        constraints = [models.UniqueConstraint(fields=["cluster", "page_type", "canonical_pattern"], name="unique_keyword_page_map")]

    def __str__(self):
        return f"{self.cluster.slug} → {self.page_type}"

    def canonical_for(self, **kwargs) -> str:
        return self.canonical_pattern.format(**kwargs)

    @property
    def is_money_page(self) -> bool:
        return self.page_type in self.MONEY_PAGE_TYPES
