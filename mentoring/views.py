from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test

from directory.models import Expertise, is_user_privileged

@user_passes_test(is_user_privileged)
def category_mentors(request, category):
    skills = Expertise.objects.of_vouched_users().filter(category=category)
    return render(request, 'mentoring/category_mentors.html', {
        'category': dict(Expertise.CATEGORY_CHOICES)[category],
        'skills': skills
    })

@user_passes_test(is_user_privileged)
def index(request):
    categories = []
    for slug, name in Expertise.CATEGORY_CHOICES:
        skills = Expertise.objects.of_vouched_users().filter(category=slug)
        categories.append({
            'slug': slug,
            'name': name,
            'count': len(skills)
        })

    return render(request, 'mentoring/index.html', {
        'categories': categories
    })
