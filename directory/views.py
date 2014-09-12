import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden, \
                        HttpResponseBadRequest
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.utils.http import urlencode
from django.db.models import Q
from django.views.decorators.clickjacking import xframe_options_exempt

from .multi_city import city_scoped, city_reverse, is_multi_city
from .models import Organization, Membership, City, is_user_vouched_for, \
                    is_user_privileged, get_current_city
from .forms import ExpertiseFormSet, ExpertiseFormSetHelper, \
                   ContentChannelFormSet, ChannelFormSetHelper, \
                   MembershipForm, UserProfileForm, OrganizationForm, \
                   UserApplicationForm

ORGS_PER_PAGE = 5

def is_request_privileged(request):
    return (request.user.is_authenticated() and
            is_user_privileged(request.user))

def validate_and_save_forms(*forms):
    forms = [form for form in forms if form is not None]
    for form in forms:
        if not form.is_valid(): return False
    for form in forms: form.save()
    return True

def home(request):
    if is_multi_city(request):
        return render(request, 'directory/multi_city_home.html', {
            'cities': City.objects.all().order_by('name')
        })
    return city_home(request)

@city_scoped
def city_home(request, city):
    all_orgs = Organization.objects.filter(
        is_active=True,
        city=city
    ).order_by('name')
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
        'city': city,
        'show_privileged_info': is_request_privileged(request)
    })

@city_scoped
def city_search(request, city):
    query = request.GET.get('query')
    if not query:
        return HttpResponseBadRequest('query must be non-empty')
    orgs = Organization.objects.filter(
        Q(name__icontains=query) |
        Q(mission__icontains=query),
        is_active=True,
        city=city
    )
    memberships = None
    if is_request_privileged(request):
        memberships = Membership.objects.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(title__icontains=query) |
            Q(bio__icontains=query),
            is_listed=True,
            user__is_active=True,
            organization__city=city
        )

    return render(request, 'directory/search.html', {
        'query': query,
        'city': city,
        'no_results': not orgs and not memberships,
        'orgs': orgs,
        'memberships': memberships
    })

@city_scoped
def city_find_json(request, city):
    query = request.GET.get('query')
    results = []
    if not query:
        return HttpResponseBadRequest('query must be non-empty')

    orgs = Organization.objects.filter(name__icontains=query,
                                       is_active=True, city=city)
    results.extend([
        {'value': org.name, 'url': org.get_absolute_url()}
        for org in orgs
    ])

    if is_request_privileged(request):
        memberships = Membership.objects.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query),
            is_listed=True,
            user__is_active=True,
            organization__city=city
        )
        results.extend([
            {'value': membership.user.get_full_name(),
             'url': membership.get_absolute_url()}
            for membership in memberships
        ])

    results.append({
        'value': 'Search the website for "%s"' % query,
        'url': '%s?%s' % (city_reverse(request, 'search'), urlencode({
            'query': query
        }))
    })

    return HttpResponse(json.dumps(results), content_type='application/json')

@city_scoped
@user_passes_test(is_user_privileged)
def city_activity(request, city):
    memberships = Membership.objects.filter(
        organization__city=city
    ).order_by('-modified')[:10]
    return render(request, 'directory/activity.html', {
        'memberships': memberships
    })

@city_scoped
def city_widgets(request, city):
    return render(request, 'directory/widgets.html', {'city': city})

@city_scoped
@xframe_options_exempt
def city_members_widget(request, city):
    orgs = Organization.objects.filter(
        is_active=True,
        city=city
    ).order_by('name')

    return render(request, 'directory/members_widget.html', {
        'orgs': orgs
    })

@city_scoped
def city_members_widget_js(request, city):
    return render(request, 'directory/members_widget.js',
                  content_type='application/javascript')

def organization_detail(request, organization_slug):
    org = get_object_or_404(Organization, slug=organization_slug,
                            is_active=True)
    return render(request, 'directory/organization_detail.html', {
        'org': org,
        'show_privileged_info': is_request_privileged(request)
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
            return redirect('organization_detail', org.slug)
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

@user_passes_test(is_user_privileged)
def user_detail(request, username):
    membership = get_object_or_404(Membership, user__username=username,
                                   user__is_active=True)
    return render(request, 'directory/user_detail.html', {
        'membership': membership
    })

@login_required
def user_apply(request):
    if request.method == 'POST':
        form = UserApplicationForm(data=request.POST)
        if form.is_valid():
            form.save(request.user)
            request.session['submitted_application'] = True
            messages.success(request,
                             'Thanks! Your request has been submitted, '
                             'and you will hear from a Hive staff member '
                             'shortly.')
            return redirect('home')
        else:
            messages.error(request, 'Your submission had some problems.')
    else:
        city = get_current_city()
        form = UserApplicationForm(initial={'city': city and city.id})
    return render(request, 'directory/user_apply.html', {
        'form': form
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
