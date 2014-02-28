from django.test import TestCase

from ..templatetags.directory import get_domainname

class TemplateTagsAndFiltersTests(TestCase):
    def test_get_domainname(self):
        self.assertEqual(get_domainname('http://foo.org:34'), 'foo.org')
