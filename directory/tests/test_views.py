import json
from django.test import TestCase
from django.contrib.auth.models import User
from registration.models import RegistrationProfile

from ..models import Organization
from ..management.commands.seeddata import create_user

get_org = lambda slug: Organization.objects.get(slug=slug)

class HomePageTests(TestCase):
    fixtures = ['wnyc.json']

    def test_requesting_empty_page_does_not_explode(self):
        response = self.client.get('/?page=9999')
        self.assertEqual(response.status_code, 200)

class WnycTestCase(TestCase):
    fixtures = ['wnyc.json']

    def login_as_non_member(self):
        self.client.login(username='non_member', password='lol')

    def login_as_wnyc_member(self):
        self.client.login(username='wnyc_member', password='lol')

    def setUp(self):
        super(WnycTestCase, self).setUp()
        self.wnyc = get_org('wnyc')
        create_user('non_member', password='lol')
        user = create_user('wnyc_member', email='member@wnyc.org',
                           password='lol', organization=self.wnyc)
        user.first_name = 'Brian'
        user.last_name = 'Lehrer'
        user.save()

class WnycAndAmnhTestCase(WnycTestCase):
    fixtures = WnycTestCase.fixtures + ['amnh.json']

    def login_as_amnh_member(self):
        self.client.login(username='amnh_member', password='lol')

    def setUp(self):
        super(WnycAndAmnhTestCase, self).setUp()
        self.amnh = get_org('amnh')
        create_user('amnh_member', email='member@amnh.org',
                    password='lol', organization=self.amnh)

class FindJsonTests(WnycTestCase):
    def query(self, query):
        response = self.client.get('/find.json', {'query': query})
        if response['Content-Type'] == 'application/json':
            response.json = json.loads(response.content)
        return response

    def test_empty_queries_fail(self):
        response = self.query('')
        self.assertEqual(response.status_code, 400)

    def test_queries_can_return_orgs(self):
        response = self.query('rookies')
        self.assertEqual(response.json, [{
            'url': '/orgs/wnyc/',
            'value': "WNYC's Radio Rookies"
        }])

    def test_unprivileged_queries_cannot_return_people(self):
        self.login_as_non_member()
        response = self.query('lehrer')
        self.assertEqual(response.json, [])

    def test_privileged_queries_can_return_people(self):
        self.login_as_wnyc_member()
        response = self.query('lehrer')
        self.assertEqual(response.json, [{
            'url': '/users/wnyc_member/',
            'value': 'Brian Lehrer'
        }])

class AccountProfileTests(WnycTestCase):
    def test_edit_org_redirects_anonymous_users_to_login(self):
        response = self.client.get('/accounts/profile/', follow=True)
        self.assertRedirects(response,
                             '/accounts/login/?next=/accounts/profile/')

    def test_profile_hides_membership_form_for_nonmembers(self):
        self.login_as_non_member()
        response = self.client.get('/accounts/profile/')
        self.assertNotContains(response, 'Membership Information')

    def test_profile_shows_membership_form_for_members(self):
        self.login_as_wnyc_member()
        response = self.client.get('/accounts/profile/')
        self.assertContains(response, 'Membership Information')

    def test_submitting_valid_form_changes_model(self):
        self.login_as_non_member()
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

class OrganizationProfileTests(WnycAndAmnhTestCase):
    def test_edit_org_redirects_anonymous_users_to_login(self):
        response = self.client.get('/orgs/wnyc/edit/', follow=True)
        self.assertRedirects(response,
                             '/accounts/login/?next=/orgs/wnyc/edit/')

    def test_edit_org_gives_non_org_members_403(self):
        self.login_as_amnh_member()
        response = self.client.get('/orgs/wnyc/edit/')
        self.assertEqual(response.status_code, 403)

    def test_edit_org_gives_org_members_200(self):
        self.login_as_wnyc_member()
        response = self.client.get('/orgs/wnyc/edit/')
        self.assertEqual(response.status_code, 200)

class OrganizationTests(WnycTestCase):
    def test_directory_listing_shows_orgs(self):
        response = self.client.get('/')
        self.assertContains(response, 'Radio Rookies')

    def test_directory_listing_shows_emails_to_members(self):
        self.login_as_wnyc_member()
        response = self.client.get('/')
        self.assertContains(response, 'member@wnyc.org')

    def test_directory_listing_hides_emails_from_nonmembers(self):
        self.login_as_non_member()
        response = self.client.get('/')
        self.assertNotContains(response, 'member@wnyc.org')

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
