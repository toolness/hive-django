import json
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from .models import Organization, City

def members(request, city):
    city = get_object_or_404(City, slug=city)
    orgs = Organization.objects.filter(
        is_active=True,
        city=city
    ).order_by('name')
    return HttpResponse(json.dumps([{
        "name": org.name,
        "website": org.website
    } for org in orgs]), content_type='application/json')
