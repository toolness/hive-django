from functools import wraps
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse

from .models import City, get_current_city

def city_scoped(f):
    @wraps(f)
    def wrapped(request, city=None, **kwargs):
        if city is None:
            # We weren't passed a city in the URL, so our request's
            # site must be associated w/ a specific city.
            city = get_current_city(request)
        else:
            # We were explicitly passed a city in the URL.
            city = get_object_or_404(City, slug=city)
        return f(request, city=city, **kwargs)
    return wrapped

def city_reverse(request, viewname):
    viewname = 'city_%s' % viewname
    if not is_multi_city(request):
        return reverse(viewname)
    return reverse(viewname, kwargs={
        'city': request.resolver_match.kwargs['city']
    })

def is_multi_city(request=None, site=None):
    return get_current_city(request, site) is None
