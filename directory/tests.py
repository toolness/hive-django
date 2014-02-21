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

class AccountProfileTests(TestCase):
    fixtures = ['wnyc.json']

    def setUp(self):
        super(AccountProfileTests, self).setUp()
        self.wnyc = Organization.objects.get(pk=1)
        create_user('non_member', password='lol')
        create_user('wnyc_member', email='member@wnyc.org', password='lol',
                    organization=self.wnyc)

    def test_edit_org_redirects_anonymous_users_to_login(self):
        c = Client()
        response = c.get('/accounts/profile/', follow=True)
        self.assertRedirects(response,
                             '/accounts/login/?next=/accounts/profile/')

    def test_profile_hides_membership_form_for_nonmembers(self):
        c = Client()
        c.login(username='wnyc_member', password='lol')
        response = c.get('/accounts/profile/')
        self.assertContains(response, 'Membership Information')

    def test_profile_shows_membership_form_for_members(self):
        c = Client()
        c.login(username='non_member', password='lol')
        response = c.get('/accounts/profile/')
        self.assertNotContains(response, 'Membership Information')

    def test_submitting_valid_form_changes_model(self):
        c = Client()
        c.login(username='non_member', password='lol')
        response = c.post('/accounts/profile/', {
            'user_profile-username': 'non_member',
            'user_profile-first_name': 'Non',
            'user_profile-last_name': 'Member'
        })
        self.assertRedirects(response, '/accounts/profile/')
        self.assertEqual(User.objects.get(username='non_member').first_name,
                         'Non')

class OrganizationProfileTests(TestCase):
    fixtures = ['wnyc.json', 'hivenyc.json']

    def setUp(self):
        super(OrganizationProfileTests, self).setUp()
        self.wnyc = Organization.objects.get(pk=1)
        self.hivenyc = Organization.objects.get(pk=2)
        create_user('non_member', password='lol')
        create_user('wnyc_member', email='member@wnyc.org', password='lol',
                    organization=self.wnyc)
        create_user('hivenyc_member', email='member@hivenyc.org',
                    password='lol', organization=self.hivenyc)

    def test_edit_org_redirects_anonymous_users_to_login(self):
        c = Client()
        response = c.get('/orgs/1/edit/', follow=True)
        self.assertRedirects(response, '/accounts/login/?next=/orgs/1/edit/')

    def test_edit_org_gives_non_org_members_403(self):
        c = Client()
        c.login(username='hivenyc_member', password='lol')
        response = c.get('/orgs/1/edit/')
        self.assertEqual(response.status_code, 403)

    def test_edit_org_gives_org_members_200(self):
        c = Client()
        c.login(username='wnyc_member', password='lol')
        response = c.get('/orgs/1/edit/')
        self.assertEqual(response.status_code, 200)

class OrganizationTests(TestCase):
    fixtures = ['wnyc.json']

    def setUp(self):
        super(OrganizationTests, self).setUp()
        self.wnyc = Organization.objects.get(pk=1)

    def test_org_has_memberships(self):
        self.assertEqual(self.wnyc.memberships.count(), 0)
        create_user('foo', organization=self.wnyc)
        self.assertEqual(self.wnyc.memberships.count(), 1)

    def test_directory_listing_shows_orgs(self):
        c = Client()
        response = c.get('/')
        self.assertContains(response, 'Radio Rookies')

    def test_directory_listing_shows_emails_to_hive_members_only(self):
        create_user('non_member', password='lol')
        create_user('member', email='member@wnyc.org', password='lol',
                    organization=self.wnyc)

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
