from django.shortcuts import render

from .models import Organization

def is_user_hive_member(user):
    return user.is_authenticated() and user.is_active and \
           user.membership.organization

def home(request):
    return render(request, 'directory/home.html', {
        'orgs': Organization.objects.all(),
        'show_privileged_info': is_user_hive_member(request.user)
    })
