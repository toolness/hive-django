from django.test import TestCase

from ..templatetags.directory import get_domainname, get_emailhash

class TemplateTagsAndFiltersTests(TestCase):
    def test_get_domainname(self):
        self.assertEqual(get_domainname('http://foo.org:34'), 'foo.org')

    def test_get_emailhash(self):
        # http://en.gravatar.com/site/implement/hash/
        self.assertEqual(get_emailhash(' MyEmailAddress@example.com'),
                         '0bc83cb571cd1c50ba6f3e8a78ef1346')
