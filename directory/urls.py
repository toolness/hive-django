from django.conf import settings
from django.conf.urls import patterns, include, url

from .multi_city import is_multi_city
from . import views

def city_scoped_directory_patterns(prefix='city'):
    return patterns('',
        url(r'^$', views.city_home, name=prefix + '_home'),
        url(r'^find.json$', views.city_find_json, name=prefix + '_find_json'),
        url(r'^search/$', views.city_search, name=prefix + '_search'),
        url(r'^activity/$', views.city_activity, name=prefix + '_activity'),
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

urlpatterns += city_scoped_directory_patterns()

urlpatterns += patterns('',
    url(r'^(?P<city>[A-Za-z0-9_\-]+)/',
        include(city_scoped_directory_patterns(prefix='multi_city')))
)
