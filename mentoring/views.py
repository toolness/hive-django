from django.shortcuts import render

from directory.models import Expertise

def category_mentors(request, category):
    skills = Expertise.objects.of_vouched_users().filter(category=category)
    return render(request, 'mentoring/category_mentors.html', {
        'category': dict(Expertise.CATEGORY_CHOICES)[category],
        'skills': skills
    })

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
