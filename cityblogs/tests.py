from django.test import TestCase
import mock

from directory.models import City
from .models import CityBlog

class OrganizationPostTests(TestCase):
    fixtures = ["wnyc.json"]

    def testReturns404WhenOrgDoesNotExist(self):
        response = self.client.get('/cityblogs/orgs/lolol')
        self.assertEqual(response.status_code, 404)

    def testReturns404WhenNoCityBlogIsDefined(self):
        response = self.client.get('/cityblogs/orgs/wnyc')
        self.assertEqual(response.status_code, 404)

    def testReturns200WhenCityBlogIsDefined(self):
        blog = CityBlog(city=City.objects.get(slug='nyc'),
                        url='http://example.org/')
        blog.save()
        feeds = {
            'entries': [
                {'published_parsed': (2013, 1, 2)}
            ]
        }
        m = mock.MagicMock(return_value=feeds)
        with mock.patch('feedparser.parse', m):
            response = self.client.get('/cityblogs/orgs/wnyc')
        m.assert_called_with('http://example.org/tag/wnyc/feed/')
        self.assertContains(response, 'January 2, 2013')
        self.assertEqual(response.status_code, 200)
