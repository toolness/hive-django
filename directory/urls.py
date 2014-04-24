from django.conf.urls import patterns, include, url

from . import views

urlpatterns = patterns('',
    url(r'^$', views.home, name='home'),
    url(r'^find.json$', views.find_json, name='find_json'),
    url(r'^orgs/(?P<organization_slug>[A-Za-z0-9_\-]+)/$',
        views.organization_detail, name='organization_detail'),
    url(r'^orgs/(?P<organization_slug>[A-Za-z0-9_\-]+)/edit/$',
        views.organization_edit, name='organization_edit'),

    # Note that this happens to be in sync with the default
    # get_absolute_url() on the User model. If this URL changes,
    # we should set settings.ABSOLUTE_URL_OVERRIDES as per
    # http://stackoverflow.com/a/2328856.
    url(r'^users/(?P<username>[A-Za-z0-9_@+.\-]+)/$',
        views.user_detail, name='user_detail'),

    url(r'^accounts/profile/$', views.user_edit, name='user_edit'),
)
