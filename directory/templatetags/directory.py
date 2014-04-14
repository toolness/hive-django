import urlparse
import hashlib
import markdown
import bleach
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='markdown')
def render_markdown(text):
    """
    Render the given markdown/HTML text as sanitized HTML.
    """

    return mark_safe(bleach.clean(
        text=markdown.markdown(text),
        tags=bleach.ALLOWED_TAGS + [
            'p'
        ]
    ))

@register.filter(name='domainname')
def get_domainname(url):
    """
    Return the domain name of the given URL.

    For example::

        {{ 'http://example.org/stuff'|domainname }}

    would display ``example.org``.
    """

    return urlparse.urlparse(url).hostname

@register.filter(name='emailhash')
def get_emailhash(email):
    """
    Return the trimmed and lowercased MD5 hash of the given
    email address. This is useful for constructing Gravatar URLs.
    """

    return hashlib.md5(email.lower().strip()).hexdigest()
