from django.conf import settings
from django.conf.urls import patterns, include, url

from .multi_city import viewname_prefix
from . import views

def city_scoped_directory_patterns(is_multi_city_site):
    prefix = viewname_prefix(is_multi_city_site)
    return patterns('',
        url(r'^$', views.city_home, name=prefix + 'home'),
        url(r'^find.json$', views.city_find_json, name=prefix + 'find_json'),
        url(r'^search/$', views.city_search, name=prefix + 'search'),
        url(r'^activity/$', views.city_activity, name=prefix + 'activity'),
    )

urlpatterns = patterns('',
    url(r'^$', views.home, name='home'),
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

urlpatterns += city_scoped_directory_patterns(is_multi_city_site=False)

urlpatterns += patterns('',
    url(r'^(?P<city>[A-Za-z0-9_\-]+)/',
        include(city_scoped_directory_patterns(is_multi_city_site=True)))
)
