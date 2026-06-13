from apps.locations.models import City


def city_selector(request):
    return {"city_selector_cities": City.objects.active()[:12]}
