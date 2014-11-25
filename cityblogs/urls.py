from django.conf.urls import patterns, include, url

from . import views

urlpatterns = patterns('',
    url(r'^orgs/(?P<organization_slug>[A-Za-z0-9_\-]+)$',
        views.organization_posts, name='cityblog_organization_posts')
)
