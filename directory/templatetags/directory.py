import urlparse
from django import template

register = template.Library()

@register.filter(name='domainname')
def get_domainname(url):
    """
    Return the domain name of the given URL.

    For example::

        {{ 'http://example.org/stuff'|domainname }}

    would display ``example.org``.
    """

    return urlparse.urlparse(url).hostname
