from django.db import models


class SearchQuery(models.Model):
    query = models.CharField(max_length=500)
    normalized_query = models.CharField(max_length=500, db_index=True)
    result_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name_plural = "search queries"

    def __str__(self):
        return f"{self.normalized_query} · {self.result_count}"

    @classmethod
    def record(cls, query: str, result_count: int):
        normalized = normalize_query(query)
        obj, _ = cls.objects.update_or_create(
            normalized_query=normalized,
            defaults={"query": query.strip(), "result_count": result_count},
        )
        return obj


def normalize_query(query: str) -> str:
    return " ".join((query or "").strip().lower().split())
