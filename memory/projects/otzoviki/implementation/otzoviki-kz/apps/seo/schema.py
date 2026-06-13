from apps.companies.models import Company
from apps.reviews.models import Review


def build_site_schema(request) -> dict:
    base_url = request.build_absolute_uri("/")
    return {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Organization",
                "@id": f"{base_url}#organization",
                "name": "Otzoviki KZ",
                "url": base_url,
            },
            {
                "@type": "WebSite",
                "@id": f"{base_url}#website",
                "name": "Otzoviki KZ",
                "url": base_url,
                "publisher": {"@id": f"{base_url}#organization"},
                "potentialAction": {
                    "@type": "SearchAction",
                    "target": request.build_absolute_uri("/search/?q={search_term_string}"),
                    "query-input": "required name=search_term_string",
                },
            },
        ],
    }


def build_company_schema(request, company: Company) -> dict | None:
    if not company.schema_eligible:
        return None
    public_reviews = list(Review.objects.public().filter(company=company))
    schema = {
        "@context": "https://schema.org",
        "@type": "HomeAndConstructionBusiness",
        "@id": request.build_absolute_uri(company.get_absolute_url()) + "#business",
        "name": company.name,
        "url": request.build_absolute_uri(company.get_absolute_url()),
        "description": company.seo_description or company.short_description,
    }
    if company.website_url:
        schema["sameAs"] = [company.website_url]
    if public_reviews:
        schema["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": round(sum(review.average_rating for review in public_reviews) / len(public_reviews), 1),
            "reviewCount": len(public_reviews),
            "bestRating": 5,
            "worstRating": 1,
        }
        schema["review"] = [build_review_schema(review) for review in public_reviews]
    return schema


def build_review_schema(review: Review) -> dict:
    return {
        "@type": "Review",
        "name": review.title,
        "reviewBody": review.body,
        "author": {"@type": "Person", "name": review.author_name},
        "reviewRating": {
            "@type": "Rating",
            "ratingValue": review.average_rating,
            "bestRating": 5,
            "worstRating": 1,
        },
        "datePublished": review.published_at.date().isoformat() if review.published_at else None,
    }
