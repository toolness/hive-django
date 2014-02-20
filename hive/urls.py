from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'directory.views.home', name='home'),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^orgs/(?P<organization_id>[0-9]+)/edit/',
        'directory.views.organization_profile', name='organization_profile'),
    url(r'^accounts/profile/', 'directory.views.user_profile',
        name='user_profile'),
    url(r'^accounts/', include('hive.account_urls')),
)
