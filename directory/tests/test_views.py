import json
from django.test import TestCase
from django.contrib.auth.models import User
from registration.models import RegistrationProfile

from ..models import Organization
from ..management.commands.seeddata import create_user

get_org = lambda slug: Organization.objects.get(slug=slug)

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

class UserDetailTests(WnycTestCase):
    def test_nonmembers_are_redirected(self):
        self.login_as_non_member()
        response = self.client.get('/users/wnyc_member/', follow=True)
        self.assertRedirects(response,
                             '/accounts/login/?next=/users/wnyc_member/')

    def test_members_are_shown_email_address(self):
        self.login_as_wnyc_member()
        response = self.client.get('/users/wnyc_member/')
        self.assertContains(response, 'member@wnyc.org')

class ActivityTests(WnycTestCase):
    def test_allows_members_to_view(self):
        self.login_as_wnyc_member()
        response = self.client.get('/activity/')
        self.assertEquals(response.status_code, 200)

    def test_redirects_nonmembers_to_login(self):
        self.login_as_non_member()
        response = self.client.get('/activity/', follow=True)
        self.assertRedirects(response,
                             '/accounts/login/?next=/activity/')

class UserEditTests(WnycTestCase):
    BASE_FORM = {
        'expertise-TOTAL_FORMS': '3',
        'expertise-INITIAL_FORMS': '0',
        'expertise-MAX_NUM_FORMS': '1000',
        'user_profile-username': 'non_member'
    }

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

    def test_submitting_invalid_form_returns_error_page(self):
        self.login_as_non_member()
        data = {'user_profile-first_name': 'WAY TOO LONG' * 1000}
        data.update(self.BASE_FORM)
        response = self.client.post('/accounts/profile/', data)
        self.assertContains(response, 'Your submission had some problems')
        self.assertContains(response, 'Ensure this value has at most 30 '
                                      'characters (it has 12000)')

    def test_submitting_valid_form_changes_model(self):
        self.login_as_non_member()
        data = {
            'user_profile-first_name': 'Non',
            'user_profile-last_name': 'Member'
        }
        data.update(self.BASE_FORM)
        response = self.client.post('/accounts/profile/', data)
        self.assertRedirects(response, '/accounts/profile/')
        self.assertEqual(User.objects.get(username='non_member').first_name,
                         'Non')

class OrganizationDetailTests(WnycTestCase):
    def test_people_are_hidden_from_non_members(self):
        self.login_as_non_member()
        response = self.client.get('/orgs/wnyc/')
        self.assertNotContains(response, 'Lehrer')

    def test_people_are_shown_to_members(self):
        self.login_as_wnyc_member()
        response = self.client.get('/orgs/wnyc/')
        self.assertContains(response, 'Lehrer')

class OrganizationEditTests(WnycAndAmnhTestCase):
    BASE_FORM = {
        'chan-TOTAL_FORMS': '3',
        'chan-INITIAL_FORMS': '0',
        'chan-MAX_NUM_FORMS': '1000'
    }

    def test_anonymous_users_are_redirected_to_login(self):
        response = self.client.get('/orgs/wnyc/edit/', follow=True)
        self.assertRedirects(response,
                             '/accounts/login/?next=/orgs/wnyc/edit/')

    def test_non_org_members_are_forbidden(self):
        self.login_as_amnh_member()
        response = self.client.get('/orgs/wnyc/edit/')
        self.assertEqual(response.status_code, 403)

    def test_org_members_can_view_page(self):
        self.login_as_wnyc_member()
        response = self.client.get('/orgs/wnyc/edit/')
        self.assertEqual(response.status_code, 200)

    def test_valid_form_submission_changes_model(self):
        self.login_as_wnyc_member()
        data = self.BASE_FORM.copy()
        data.update({
            'org-name': 'Awesome WNYC',
            'org-website': 'http://awesomewnyc.org/'
        })
        response = self.client.post('/orgs/wnyc/edit/', data, follow=True)
        self.assertRedirects(response, '/orgs/wnyc/')
        self.assertContains(response,
                            'The organization profile has been updated')
        self.assertEqual(get_org('wnyc').name, 'Awesome WNYC')

    def test_invalid_form_submission_returns_error_page(self):
        self.login_as_wnyc_member()
        data = self.BASE_FORM.copy()
        response = self.client.post('/orgs/wnyc/edit/', data)
        self.assertContains(response, 'Your submission had some problems')
        self.assertContains(response, 'This field is required')

class HomePageTests(WnycTestCase):
    def test_requesting_empty_page_does_not_explode(self):
        response = self.client.get('/?page=9999')
        self.assertEqual(response.status_code, 200)

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
