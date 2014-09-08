import json

from django.test import TestCase

class ApiTests(TestCase):
    fixtures = ['wnyc.json', 'amnh.json']

    def get_json(self, url):
        response = self.client.get(url)
        if response['Content-Type'] == 'application/json':
            response.json = json.loads(response.content)
        return response

    def test_members(self):
        response = self.get_json('/api/v1/cities/nyc/members')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [
            {"name": "American Museum of Natural History",
             "website": "http://www.amnh.org/"},
            {"name": "WNYC's Radio Rookies",
             "website": "http://www.radiorookies.org/"},
        ])
