import urlparse
import hashlib
import markdown
import bleach
from django import template
from django.utils.safestring import mark_safe

from ..multi_city import city_reverse

register = template.Library()

ALLOWED_ATTRIBUTES = bleach.ALLOWED_ATTRIBUTES.copy()

ALLOWED_ATTRIBUTES.update(**{
    'img': ['src', 'alt']
})

@register.simple_tag(takes_context=True)
def city_url(context, viewname):
    """
    Like the ``url`` template tag, but specifically for any view
    name beginning with ``city_``. This is required because depending
    on the configuration of the site, city URLs may need to contain
    the name of a city in them, which this template tag does for you.
    """

    request = context.get('request')
    if request is None:
        raise Exception('django.core.context_processors.request must '
                        'be installed.')
    return city_reverse(request, viewname)

@register.filter(name='markdown')
def render_markdown(text):
    """
    Render the given markdown/HTML text as sanitized HTML.
    """

    return mark_safe(bleach.clean(
        text=markdown.markdown(text),
        tags=bleach.ALLOWED_TAGS + [
            'p',
            'pre',
            'img'
        ],
        attributes=ALLOWED_ATTRIBUTES
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
