from django.shortcuts import render, redirect
from django.forms import ModelForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from .models import Organization, Membership

class MembershipForm(ModelForm):
    class Meta:
        model = Membership
        fields = ['title', 'is_listed']

class UserProfileForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']

def validate_and_save_forms(*forms):
    forms = [form for form in forms if form is not None]
    for form in forms:
        if not form.is_valid(): return False
    for form in forms: form.save()
    return True

def is_user_hive_member(user):
    return user.is_authenticated() and user.is_active and \
           user.membership.organization

def home(request):
    return render(request, 'directory/home.html', {
        'orgs': Organization.objects.all(),
        'show_privileged_info': is_user_hive_member(request.user)
    })

@login_required
def user_profile(request):
    user = request.user
    membership_form = None
    data = None

    if request.method == 'POST': data = request.POST
    if is_user_hive_member(user):
        membership_form = MembershipForm(data=data,
                                         instance=user.membership,
                                         prefix='membership')
    user_profile_form = UserProfileForm(data=data,
                                        instance=user,
                                        prefix='user_profile')
    if request.method == 'POST':
        if validate_and_save_forms(user_profile_form, membership_form):
            messages.success(request, 'Your profile has been updated.')
        else:
            messages.error(request, 'Your submission had some problems.')
        return redirect('user_profile')

    return render(request, 'directory/user_profile.html', {
        'membership_form': membership_form,
        'user_profile_form': user_profile_form
    })
