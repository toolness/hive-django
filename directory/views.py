from django.shortcuts import render

from .models import Organization

def home(request):
    return render(request, 'directory/home.html', {
        'orgs': Organization.objects.all()
    })
