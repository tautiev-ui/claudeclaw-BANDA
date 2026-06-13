from django.db import models

from apps.locations.models import City


class ActiveServiceQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True, category__is_active=True).select_related("category").order_by("name")


class ServiceCategory(models.Model):
    name = models.CharField(max_length=140)
    slug = models.SlugField(max_length=140, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "service categories"

    def __str__(self):
        return self.name


class Service(models.Model):
    category = models.ForeignKey(ServiceCategory, on_delete=models.PROTECT, related_name="services")
    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=160, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ActiveServiceQuerySet.as_manager()

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self, city: City) -> str:
        return f"{city.get_absolute_url()}{self.slug}/"

    def ranking_url(self, city: City) -> str:
        return f"{city.get_absolute_url()}reyting-remontnyh-kompaniy/"

    def price_url(self, city: City) -> str:
        return f"{self.get_absolute_url(city)}ceny/"

    def public_label(self, city: City) -> str:
        return f"{self.name} в {city.name}"
