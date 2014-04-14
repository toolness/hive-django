from django.test import TestCase
from django.utils.safestring import SafeData

from ..templatetags.directory import get_domainname, get_emailhash, \
                                     render_markdown

class TemplateTagsAndFiltersTests(TestCase):
    def test_get_domainname(self):
        self.assertEqual(get_domainname('http://foo.org:34'), 'foo.org')

    def test_get_emailhash(self):
        # http://en.gravatar.com/site/implement/hash/
        self.assertEqual(get_emailhash(' MyEmailAddress@example.com'),
                         '0bc83cb571cd1c50ba6f3e8a78ef1346')

class MarkdownRenderingTests(TestCase):
    def assertRendering(self, markdown, rendering):
        self.assertEqual(render_markdown(markdown), rendering)

    def test_accepts_p_tags(self):
        self.assertRendering('hello', '<p>hello</p>')

    def test_accepts_markdown_emphasis(self):
        self.assertRendering('*hello*', '<p><em>hello</em></p>')

    def test_accepts_em_tags(self):
        self.assertRendering('<em>hello</em>', '<p><em>hello</em></p>')

    def test_escapes_script_tags(self):
        self.assertRendering('<script>h</script>',
                             '&lt;script&gt;h&lt;/script&gt;')

    def test_returns_safedata(self):
        self.assertTrue(isinstance(render_markdown('p'), SafeData))
