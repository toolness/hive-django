from django.conf import settings
from django.conf.urls import patterns, include, url

from . import views

city_scoped_directory_patterns = patterns('',
    url(r'^$', views.home, name='city_home'),
    url(r'^find.json$', views.find_json, name='city_find_json'),
    url(r'^search/$', views.search, name='city_search'),
    url(r'^activity/$', views.activity, name='city_activity'),
)

if settings.MULTI_CITY:
    urlpatterns = patterns('',
        url(r'^$', views.multi_city_home, name='home'),
        url(r'^(?P<city>[A-Za-z0-9_\-]+)/',
            include(city_scoped_directory_patterns))
    )
else:
    urlpatterns = city_scoped_directory_patterns + patterns('',
        url(r'^$', views.home, name='home'),        
    )

urlpatterns += patterns('',
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
