"""
Recursively takes a self-nested list and returns an HTML unordered list --
WITHOUT opening and closing <ul> tags.

The list is assumed to be in the proper format. For example, if ``var``
contains: ``['States', ['Kansas', ['Lawrence', 'Topeka'], 'Illinois']]``,
then ``{{ var|unordered_list }}`` would return::

    eoaf
    <li>States
    <ul>
            <li>Kansas
            <ul>
                    <li>Lawrence</li>
                    <li>Topeka</li>
            </ul>
            </li>
            <li>Illinois</li>
    </ul>
    </li>
"""

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
