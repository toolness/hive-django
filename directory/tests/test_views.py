from django.test import TestCase
from django.contrib.auth.models import User
from registration.models import RegistrationProfile

from ..models import Organization
from ..management.commands.seeddata import create_user

get_org = lambda slug: Organization.objects.get(slug=slug)

class AccountProfileTests(TestCase):
    fixtures = ['wnyc.json']

    def setUp(self):
        super(AccountProfileTests, self).setUp()
        self.wnyc = get_org('wnyc')
        create_user('non_member', password='lol')
        create_user('wnyc_member', email='member@wnyc.org', password='lol',
                    organization=self.wnyc)

    def test_edit_org_redirects_anonymous_users_to_login(self):
        response = self.client.get('/accounts/profile/', follow=True)
        self.assertRedirects(response,
                             '/accounts/login/?next=/accounts/profile/')

    def test_profile_hides_membership_form_for_nonmembers(self):
        self.client.login(username='wnyc_member', password='lol')
        response = self.client.get('/accounts/profile/')
        self.assertContains(response, 'Membership Information')

    def test_profile_shows_membership_form_for_members(self):
        self.client.login(username='non_member', password='lol')
        response = self.client.get('/accounts/profile/')
        self.assertNotContains(response, 'Membership Information')

    def test_submitting_valid_form_changes_model(self):
        self.client.login(username='non_member', password='lol')
        response = self.client.post('/accounts/profile/', {
            'expertise-TOTAL_FORMS': '3',
            'expertise-INITIAL_FORMS': '0',
            'expertise-MAX_NUM_FORMS': '1000',
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
        self.wnyc = get_org('wnyc')
        self.hivenyc = get_org('hivenyc')
        create_user('non_member', password='lol')
        create_user('wnyc_member', email='member@wnyc.org', password='lol',
                    organization=self.wnyc)
        create_user('hivenyc_member', email='member@hivenyc.org',
                    password='lol', organization=self.hivenyc)

    def test_edit_org_redirects_anonymous_users_to_login(self):
        response = self.client.get('/orgs/wnyc/edit/', follow=True)
        self.assertRedirects(response,
                             '/accounts/login/?next=/orgs/wnyc/edit/')

    def test_edit_org_gives_non_org_members_403(self):
        self.client.login(username='hivenyc_member', password='lol')
        response = self.client.get('/orgs/wnyc/edit/')
        self.assertEqual(response.status_code, 403)

    def test_edit_org_gives_org_members_200(self):
        self.client.login(username='wnyc_member', password='lol')
        response = self.client.get('/orgs/wnyc/edit/')
        self.assertEqual(response.status_code, 200)

class OrganizationTests(TestCase):
    fixtures = ['wnyc.json']

    def setUp(self):
        super(OrganizationTests, self).setUp()
        self.wnyc = get_org('wnyc')

    def test_directory_listing_shows_orgs(self):
        response = self.client.get('/')
        self.assertContains(response, 'Radio Rookies')

    def test_directory_listing_shows_emails_to_hive_members_only(self):
        create_user('non_member', password='lol')
        create_user('member', email='member@wnyc.org', password='lol',
                    organization=self.wnyc)

        c = self.client
        c.login(username='non_member', password='lol')
        response = c.get('/')
        self.assertNotContains(response, 'member@wnyc.org')

        c.login(username='member', password='lol')
        response = c.get('/')
        self.assertContains(response, 'member@wnyc.org')

class ActivationTests(TestCase):
    fixtures = ['wnyc.json']

    def activate_user(self, *args, **kwargs):
        user = create_user(is_active=False, *args, **kwargs)
        profile = RegistrationProfile.objects.create_profile(user)
        c = self.client
        response = c.get('/accounts/activate/%s/' % profile.activation_key)
        self.assertRedirects(response, '/accounts/activate/complete/')
        user = User.objects.get(username='somebody')
        self.assertEqual(user.is_active, True)
        return user

    def test_user_org_is_blank_on_activation_if_email_does_not_match(self):
        user = self.activate_user('somebody', password='lol',
                                  email='somebody@example.org')
        self.assertEqual(user.membership.organization, None)

    def test_user_org_is_assigned_on_activation_if_email_matches(self):
        user = self.activate_user('somebody', password='lol',
                                  email='somebody@wnyc.org')
        self.assertEqual(user.membership.organization.slug, 'wnyc')
