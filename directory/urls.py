from django.conf.urls import patterns, include, url

from . import views

urlpatterns = patterns('',
    url(r'^$', views.home, name='home'),
    url(r'^o/(?P<organization_slug>[A-Za-z0-9_\-]+)/$',
        views.organization_detail, name='organization_detail'),
    url(r'^o/(?P<organization_slug>[A-Za-z0-9_\-]+)/edit/$',
        views.organization_edit, name='organization_edit'),
    # Usernames may contain alphanumeric, _, @, +, . and - characters.
    url(r'^u/(?P<username>[A-Za-z0-9_@+.\-]+)/$',
        views.user_detail, name='user_detail'),
    url(r'^accounts/profile/$', views.user_edit, name='user_edit'),
)
