from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

from apps.companies.models import Company
from apps.guides.models import Guide
from apps.locations.models import City
from apps.reviews.models import RatingSnapshot


def health(request):
    return JsonResponse({
        'status': 'ok',
        'service': 'otzoviki-kz',
        'time': timezone.now().isoformat(),
    })


def home(request):
    companies = list(Company.objects.filter(is_active=True).order_by('name')[:6])
    snapshots = {snapshot.company_id: snapshot for snapshot in RatingSnapshot.objects.filter(company__in=companies)}
    company_cards = [{"company": company, "snapshot": snapshots.get(company.id)} for company in companies]
    return render(request, 'home.html', {
        'page_title': 'Otzoviki KZ — проверка ремонтных компаний',
        'page_description': 'Проверка ремонтных компаний Казахстана: отзывы, досье, внешний след, методология и право на ответ.',
        'canonical_url': request.build_absolute_uri('/'),
        'robots_meta': 'index,follow',
        'cities': City.objects.active()[:8],
        'company_cards': company_cards,
        'guides': Guide.objects.public()[:4],
    })
