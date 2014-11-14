from django.test import TestCase
from django.contrib.sites.models import Site
from django.test.utils import override_settings

from ..multi_city import is_multi_city

def using_multi_city_site(f):
    def wrapper(self):
        site = Site(domain='globalhivedir.com', name='Global Hive Dir')
        site.save()
        with override_settings(SITE_ID=site.id):
            return f(self)
    return wrapper

class IsMultiCityTests(TestCase):
    fixtures = ['wnyc.json']

    @using_multi_city_site
    def test_returns_true_when_city_does_not_exist(self):
        self.assertTrue(is_multi_city())

    def test_returns_false_when_city_exists(self):
        self.assertFalse(is_multi_city())

class CityScopedTests(TestCase):
    fixtures = ['wnyc.json', 'chicago.json']

    def test_single_city_sites_ignore_multi_city_urls(self):
        response = self.client.get('/chicago/')
        self.assertEqual(response.status_code, 404)

    def test_single_city_sites_accept_single_city_urls(self):
        response = self.client.get('/activity/')
        self.assertEqual(response.status_code, 302)

    @using_multi_city_site
    def test_multi_city_sites_accept_multi_city_urls(self):
        response = self.client.get('/chicago/')
        self.assertEqual(response.status_code, 200)

    @using_multi_city_site
    def test_multi_city_sites_404_on_invalid_city_slugs(self):
        response = self.client.get('/podunk/')
        self.assertEqual(response.status_code, 404)

    @using_multi_city_site
    def test_multi_city_sites_ignore_single_city_urls(self):
        response = self.client.get('/activity/')
        self.assertEqual(response.status_code, 404)
