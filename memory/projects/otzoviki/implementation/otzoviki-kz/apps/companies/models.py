from django.db import models
from django.core.exceptions import ValidationError

from apps.locations.models import City
from apps.seo.indexability import IndexabilityStatus
from apps.seo.models import SEOFieldsMixin
from apps.services.models import Service


class Company(SEOFieldsMixin):
    class ProfileStatus(models.TextChoices):
        UNCLAIMED = "unclaimed", "unclaimed"
        CLAIMED = "claimed", "claimed"
        VERIFIED = "verified", "verified"
        DISPUTED = "disputed", "disputed"

    name = models.CharField(max_length=220)
    slug = models.SlugField(max_length=240, unique=True)
    profile_status = models.CharField(max_length=24, choices=ProfileStatus.choices, default=ProfileStatus.UNCLAIMED)
    short_description = models.TextField(blank=True)
    website_url = models.URLField(blank=True)
    phone = models.CharField(max_length=64, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "companies"

    def __str__(self):
        return self.name

    def get_absolute_url(self) -> str:
        return f"/kz/company/{self.slug}/"

    @property
    def profile_status_label(self) -> str:
        return self.profile_status

    def clean(self):
        super().clean()
        if self.index_status != IndexabilityStatus.INDEXABLE:
            return
        missing = []
        if not self.seo_title:
            missing.append("seo_title")
        if not self.seo_description:
            missing.append("seo_description")
        if self.source_count <= 0:
            missing.append("source_count")
        if not self.last_verified_at:
            missing.append("last_verified_at")
        if not self.methodology_version:
            missing.append("methodology_version")
        if missing:
            raise ValidationError({"index_status": f"Cannot mark company indexable while required fields are missing: {', '.join(missing)}"})


class CompanyService(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="service_links")
    city = models.ForeignKey(City, on_delete=models.PROTECT, related_name="company_service_links")
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name="company_service_links")
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["company__name", "city__name", "service__name"]
        constraints = [
            models.UniqueConstraint(fields=["company", "city", "service"], name="unique_company_city_service")
        ]

    def __str__(self):
        return f"{self.company.name} · {self.service.name} · {self.city.name}"

    @property
    def service_page_url(self) -> str:
        return self.service.get_absolute_url(self.city)

    @property
    def company_url(self) -> str:
        return self.company.get_absolute_url()
