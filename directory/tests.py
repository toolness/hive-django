from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .templatetags.directory import get_domainname
from .models import Organization
from .twitter import validate_twitter_name

def create_user(username, password=None, organization=None, **kwargs):
    user = User(username=username, **kwargs)
    if password:
        user.set_password(password)
    user.save()
    if organization:
        user.membership.organization = organization
        user.membership.save()
    return user

class OrganizationTests(TestCase):
    fixtures = ['radio-rookies.json']

    def test_org_has_memberships(self):
        org = Organization.objects.get(pk=1)
        self.assertEqual(org.memberships.count(), 0)
        create_user('foo', organization=org)
        self.assertEqual(org.memberships.count(), 1)

    def test_directory_listing_shows_orgs(self):
        c = Client()
        response = c.get('/')
        self.assertContains(response, 'Radio Rookies')

    def test_directory_listing_shows_emails_to_hive_members_only(self):
        create_user('non_member', password='lol')
        create_user('member', email='member@wnyc.org', password='lol',
                    organization=Organization.objects.get(pk=1))

        c = Client()
        c.login(username='non_member', password='lol')
        response = c.get('/')
        self.assertNotContains(response, 'member@wnyc.org')

        c.login(username='member', password='lol')
        response = c.get('/')
        self.assertContains(response, 'member@wnyc.org')

class MembershipTests(TestCase):
    def test_user_membership_is_created_on_save(self):
        user = User(username='foo')
        user.save()
        self.assertTrue(user.membership)
        self.assertTrue(user.membership.is_listed)
        self.assertFalse(user.membership.organization)

class TwitterNameTests(TestCase):
    def test_validate_twitter_name_rejects_invalid_names(self):
        self.assertRaises(ValidationError, validate_twitter_name, '$')
        self.assertRaises(ValidationError, validate_twitter_name,
                          'reallyreallyreallyreallylongusername')

    def test_validate_twitter_name_accepts_valid_names(self):
        validate_twitter_name('toolness')
        validate_twitter_name('t')
        validate_twitter_name('super_burger')

class TemplateTagsAndFiltersTests(TestCase):
    def test_get_domainname(self):
        self.assertEqual(get_domainname('http://foo.org:34'), 'foo.org')
