from functools import wraps
from django.conf import settings
from django.contrib.sites.models import get_current_site
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse

from .models import City

def city_scoped(f):
    @wraps(f)
    def wrapped(request, city=None, **kwargs):
        if city is None:
            # We weren't passed a city in the URL, so our request's
            # site must be associated w/ a specific city.
            assert(not settings.MULTI_CITY)
            city = get_current_site(request).city
        else:
            # We were explicitly passed a city in the URL.
            assert(settings.MULTI_CITY)
            city = get_object_or_404(City, slug=city)
        return f(request, city=city, **kwargs)
    return wrapped

def city_reverse(request, viewname):
    viewname = 'city_%s' % viewname
    if not settings.MULTI_CITY:
        return reverse(viewname)
    return reverse(viewname, kwargs={
        'city': request.resolver_match.kwargs['city']
    })
