from django.conf.urls import patterns, include, url

from directory.models import Expertise
from . import views

urlpatterns = patterns('',
    url(r'^$', views.index),
    url(r'^(?P<category>' + 
        '|'.join(dict(Expertise.CATEGORY_CHOICES).keys()) + 
        ')/$', views.category_mentors)
)
