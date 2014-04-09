import urlparse
import hashlib
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

@register.filter(name='emailhash')
def get_emailhash(email):
    """
    Return the trimmed and lowercased MD5 hash of the given
    email address. This is useful for constructing Gravatar URLs.
    """

    return hashlib.md5(email.lower().strip()).hexdigest()
