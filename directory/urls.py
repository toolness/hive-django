from django.conf.urls import patterns, include, url

from . import views

urlpatterns = patterns('',
    url(r'^$', views.home, name='home'),
    url(r'^orgs/(?P<organization_slug>[A-Za-z0-9_\-]+)/edit/',
        views.organization_edit, name='organization_edit'),
    url(r'^accounts/profile/', views.user_edit, name='user_edit'),
)
