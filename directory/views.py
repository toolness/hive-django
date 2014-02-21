from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.forms import ModelForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from .models import Organization, Membership, is_user_hive_member

class MembershipForm(ModelForm):
    class Meta:
        model = Membership
        fields = ['title', 'is_listed']
        labels = {
            'is_listed': 'List me under my organization\'s entry in the '
                         'Hive member directory.'
        }
        help_texts = {
            'is_listed': '',
            'title': 'Your title at your organization, e.g. '
                     '"Executive Director of Awesome".'
        }

class UserProfileForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']

class OrganizationForm(ModelForm):
    class Meta:
        model = Organization
        fields = ['name', 'website', 'address', 'twitter_name',
                  'hive_member_since', 'mission']

def validate_and_save_forms(*forms):
    forms = [form for form in forms if form is not None]
    for form in forms:
        if not form.is_valid(): return False
    for form in forms: form.save()
    return True

def home(request):
    return render(request, 'directory/home.html', {
        'orgs': Organization.objects.all(),
        'show_privileged_info': request.user.is_authenticated()
                                and is_user_hive_member(request.user)
    })

@login_required
def organization_profile(request, organization_slug):
    org = get_object_or_404(Organization, slug=organization_slug)
    user = request.user
    if not (user.is_superuser or is_user_hive_member(user, org)):
        return HttpResponseForbidden('Permission denied.')
    if request.method == 'POST':
        form = OrganizationForm(request.POST, instance=org)
        if form.is_valid():
            form.save()
            messages.success(request,
                             'The organization profile has been updated.')
            return redirect('organization_profile', org.slug)
        else:
            messages.error(request, 'Your submission had some problems.')
    else:
        form = OrganizationForm(instance=org)
    return render(request, 'directory/organization_profile.html', {
        'org': org,
        'form': form
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
            return redirect('user_profile')
        else:
            messages.error(request, 'Your submission had some problems.')

    return render(request, 'directory/user_profile.html', {
        'membership_form': membership_form,
        'user_profile_form': user_profile_form
    })
