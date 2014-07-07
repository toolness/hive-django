from django.test import TestCase
from django.contrib.sites.models import Site

from ..multi_city import is_multi_city

class MultiCityTests(TestCase):
    def test_is_multi_city_returns_true_when_city_does_not_exist(self):
        site = Site(name='Foo', domain='foo.com')
        self.assertTrue(is_multi_city(site=site))

    def test_is_multi_city_returns_false_when_city_exists(self):
        # By default, we have a single default city associated w/ the 
        # single default site, so is_multi_city() will use that.
        self.assertFalse(is_multi_city())
