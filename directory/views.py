from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Organization, is_user_vouched_for, \
                    is_user_privileged
from .forms import ExpertiseFormSet, ExpertiseFormSetHelper, \
                   ContentChannelFormSet, ChannelFormSetHelper, \
                   MembershipForm, UserProfileForm, OrganizationForm

ORGS_PER_PAGE = 5

def validate_and_save_forms(*forms):
    forms = [form for form in forms if form is not None]
    for form in forms:
        if not form.is_valid(): return False
    for form in forms: form.save()
    return True

def home(request):
    all_orgs = Organization.objects.filter(is_active=True).order_by('name')
    paginator = Paginator(all_orgs, ORGS_PER_PAGE)

    page = request.GET.get('page')
    try:
        orgs = paginator.page(page)
    except PageNotAnInteger:
        orgs = paginator.page(1)
    except EmptyPage:
        orgs = paginator.page(paginator.num_pages)

    return render(request, 'directory/home.html', {
        'orgs': orgs,
        'show_privileged_info': request.user.is_authenticated()
                                and is_user_privileged(request.user)
    })

@login_required
def organization_edit(request, organization_slug):
    org = get_object_or_404(Organization, slug=organization_slug,
                            is_active=True)
    user = request.user
    if not (user.is_superuser or is_user_vouched_for(user, org)):
        return HttpResponseForbidden('Permission denied.')
    if request.method == 'POST':
        form = OrganizationForm(request.POST, instance=org, prefix='org')
        channel_formset = ContentChannelFormSet(request.POST, instance=org,
                                                prefix='chan')
        if form.is_valid() and channel_formset.is_valid():
            form.save()
            channel_formset.save()
            messages.success(request,
                             'The organization profile has been updated.')
            return redirect('organization_edit', org.slug)
        else:
            messages.error(request, 'Your submission had some problems.')
    else:
        form = OrganizationForm(instance=org, prefix='org')
        channel_formset = ContentChannelFormSet(instance=org, prefix='chan')
    channel_formset_helper = ChannelFormSetHelper()
    return render(request, 'directory/organization_edit.html', {
        'org': org,
        'form': form,
        'channel_formset': channel_formset,
        'channel_formset_helper': channel_formset_helper
    })

@login_required
def user_edit(request):
    user = request.user
    membership_form = None
    data = None

    if request.method == 'POST': data = request.POST
    if is_user_vouched_for(user):
        membership_form = MembershipForm(data=data,
                                         instance=user.membership,
                                         prefix='membership')
    user_profile_form = UserProfileForm(data=data,
                                        instance=user,
                                        prefix='user_profile')
    expertise_formset = ExpertiseFormSet(data=data, instance=user,
                                         prefix='expertise')
    if request.method == 'POST':
        if validate_and_save_forms(user_profile_form, membership_form,
                                   expertise_formset):
            messages.success(request, 'Your profile has been updated.')
            return redirect('user_edit')
        else:
            messages.error(request, 'Your submission had some problems.')

    return render(request, 'directory/user_edit.html', {
        'membership_form': membership_form,
        'user_profile_form': user_profile_form,
        'expertise_formset': expertise_formset,
        'expertise_formset_helper': ExpertiseFormSetHelper()
    })
