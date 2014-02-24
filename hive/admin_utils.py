from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib import auth
from django.contrib.auth.decorators import user_passes_test, login_required

def _switch_to(request, user):
    # http://stackoverflow.com/a/2787747
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    auth.login(request, user)

@require_POST
@user_passes_test(lambda u: u.is_active and u.is_superuser)
def switch_user(request, username):
    superuser_name = request.user.username
    user = get_object_or_404(User, username=username)

    _switch_to(request, user)
    request.session['user_switched_from'] = superuser_name

    messages.success(request, 'You are now logged in as %s.' % username)

    return redirect('home')

@require_POST
@login_required
def switch_user_back(request):
    superuser_name = request.session.get('user_switched_from')
    if superuser_name:
        user = User.objects.get(username=superuser_name, is_active=True,
                                is_superuser=True)
        _switch_to(request, user)
    return redirect('home')
