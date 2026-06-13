from django.db import models


class ActiveCityQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True, country__is_active=True).order_by("name")


class Country(models.Model):
    code = models.CharField(max_length=8, unique=True)
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=64, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "countries"

    def __str__(self):
        return self.name

    def get_absolute_url(self) -> str:
        return f"/{self.slug}/"


class City(models.Model):
    country = models.ForeignKey(Country, on_delete=models.PROTECT, related_name="cities")
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=120)
    region = models.CharField(max_length=160, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ActiveCityQuerySet.as_manager()

    class Meta:
        ordering = ["name"]
        unique_together = [("country", "slug")]
        verbose_name_plural = "cities"

    def __str__(self):
        return self.name

    @property
    def public_label(self) -> str:
        return f"{self.name}, {self.country.name}"

    def get_absolute_url(self) -> str:
        return f"/{self.country.slug}/{self.slug}/"
