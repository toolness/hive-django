from functools import wraps
from django.http import HttpResponseNotFound
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse

from .models import City, get_current_city

def city_scoped(f):
    @wraps(f)
    def wrapped(request, city=None, **kwargs):
        site_city = get_current_city(request)
        if city is None:
            # We weren't passed a city in the URL, so our request's
            # site should be associated w/ a specific city...
            if site_city is None:
                # ... but if not, just return 404.
                return HttpResponseNotFound()
            city = site_city
        else:
            # We were explicitly passed a city in the URL.
            if site_city:
                # But if we're a single-city site, return 404.
                return HttpResponseNotFound()
            city = get_object_or_404(City, slug=city)
        return f(request, city=city, **kwargs)
    return wrapped

def city_reverse(request, viewname):
    if not is_multi_city(request):
        return reverse('city_%s' % viewname)
    return reverse('multi_city_%s' % viewname, kwargs={
        'city': request.resolver_match.kwargs['city']
    })

def is_multi_city(request=None, site=None):
    return get_current_city(request, site) is None
