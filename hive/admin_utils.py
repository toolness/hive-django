from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib import auth
from django.contrib.auth.decorators import user_passes_test

@require_POST
@user_passes_test(lambda u: u.is_active and u.is_superuser)
def switch_user(request, username):
    user = get_object_or_404(User, username=username)

    # http://stackoverflow.com/a/2787747
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    auth.login(request, user)

    messages.success(request, 'You are now logged in as %s.' % username)

    return redirect('home')
