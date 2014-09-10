import json
from django.test import TestCase
from django.contrib.auth.models import User
from django.core import mail
from registration.models import RegistrationProfile

from .test_multi_city import using_multi_city_site
from ..models import Organization
from ..management.commands.seeddata import create_user

get_org = lambda slug: Organization.objects.get(slug=slug)

class WnycTestCase(TestCase):
    fixtures = ['wnyc.json']

    def login_as_non_member(self):
        self.client.login(username='non_member', password='lol')

    def login_as_wnyc_member(self):
        self.client.login(username='wnyc_member', password='lol')

    def assertNonMembersAreDenied(self, url):
        self.login_as_non_member()
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, '/accounts/login/?next=' + url)

    def setUp(self):
        super(WnycTestCase, self).setUp()
        self.wnyc = get_org('wnyc')
        self.non_member = create_user('non_member', password='lol')
        user = create_user('wnyc_member', email='member@wnyc.org',
                           password='lol', organization=self.wnyc)
        user.first_name = 'Brian'
        user.last_name = 'Lehrer'
        user.save()
        self.wnyc_member = user

class WnycAndAmnhTestCase(WnycTestCase):
    fixtures = WnycTestCase.fixtures + ['amnh.json']

    def login_as_amnh_member(self):
        self.client.login(username='amnh_member', password='lol')

    def setUp(self):
        super(WnycAndAmnhTestCase, self).setUp()
        self.amnh = get_org('amnh')
        create_user('amnh_member', email='member@amnh.org',
                    password='lol', organization=self.amnh)

class SearchTests(WnycTestCase):
    def query(self, query, ignore_last_result=True):
        return self.client.get('/search/', {'query': query})

    def test_empty_queries_fail(self):
        response = self.query('')
        self.assertEqual(response.status_code, 400)

    def test_queries_can_return_no_results(self):
        response = self.query('asdf')
        self.assertContains(response, "no results matched your query")

    def test_queries_can_return_orgs(self):
        response = self.query('rookies')
        self.assertContains(response, "Radio Rookies")

    def test_unprivileged_queries_cannot_return_people(self):
        self.login_as_non_member()
        response = self.query('lehrer')
        self.assertNotContains(response, 'Brian Lehrer')

    def test_privileged_queries_can_return_people(self):
        self.login_as_wnyc_member()
        response = self.query('lehrer')
        self.assertContains(response, 'Brian Lehrer')

class FindJsonTests(WnycTestCase):
    def query(self, query, ignore_last_result=True):
        response = self.client.get('/find.json', {'query': query})
        if response['Content-Type'] == 'application/json':
            response.json = json.loads(response.content)
            if ignore_last_result:
                response.json = response.json[:-1]
        return response

    def test_empty_queries_fail(self):
        response = self.query('')
        self.assertEqual(response.status_code, 400)

    def test_last_result_is_to_search(self):
        response = self.query('blarg u', ignore_last_result=False)
        self.assertEqual(response.json, [{
            'url': '/search/?query=blarg+u',
            'value': 'Search the website for "blarg u"'
        }])        

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
        self.assertNonMembersAreDenied('/users/wnyc_member/')

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
        self.assertNonMembersAreDenied('/activity/')

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

    @using_multi_city_site
    def test_multi_city_homepage_shows_cities(self):
        response = self.client.get('/')
        self.assertContains(response, 'New York City')
        self.assertNotContains(response, 'Radio Rookies')

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

    def test_user_org_is_blank_if_email_matches_multiple_orgs(self):
        Organization(name='WNYC Radio Grizzled Veterans',
                     city=Organization.objects.get(slug='wnyc').city,
                     email_domain='wnyc.org').save()

        user = self.activate_user('somebody', password='lol',
                                  email='somebody@wnyc.org')
        self.assertEqual(user.membership.organization, None)

    def test_user_org_is_blank_on_activation_if_email_does_not_match(self):
        user = self.activate_user('somebody', password='lol',
                                  email='somebody@example.org')
        self.assertEqual(user.membership.organization, None)

    def test_user_org_is_assigned_on_activation_if_email_matches(self):
        user = self.activate_user('somebody', password='lol',
                                  email='somebody@wnyc.org')
        self.assertEqual(user.membership.organization.slug, 'wnyc')

class UserApplyTests(WnycTestCase):
    ALREADY_MEMBER_TEXT = 'You are already a member'
    NOT_ALREADY_MEMBER_TEXT = 'please fill out the form below'
    FILL_NAME_TEXT = 'Please fill out your name'
    APPLY_TEXT = 'apply for full access'
    APP_REJECTED_TEXT = 'Your submission had some problems.'
    APP_REJECTED_FIELD_TEXT = 'This field is required.'
    APP_SENT_TEXT = 'Your request has been submitted'
    NO_STAFF_TEXT = 'because there are no Hive staff members for'

    def test_members_are_not_sent_to_application(self):
        self.login_as_wnyc_member()
        response = self.client.get('/')
        self.assertNotContains(response, self.FILL_NAME_TEXT)
        self.assertNotContains(response, self.APPLY_TEXT)

    def test_nonmembers_are_sent_to_application(self):
        self.login_as_non_member()
        response = self.client.get('/')
        self.assertContains(response, self.FILL_NAME_TEXT)
        self.assertNotContains(response, self.APPLY_TEXT)

        self.non_member.first_name = 'Bob'
        self.non_member.save()
        response = self.client.get('/')
        self.assertNotContains(response, self.FILL_NAME_TEXT)
        self.assertContains(response, self.APPLY_TEXT)

    def test_members_cannot_apply(self):
        self.login_as_wnyc_member()
        response = self.client.get('/accounts/apply/')
        self.assertContains(response, self.ALREADY_MEMBER_TEXT)
        self.assertNotContains(response, self.NOT_ALREADY_MEMBER_TEXT)

    def test_nonmembers_can_apply(self):
        self.login_as_non_member()
        response = self.client.get('/accounts/apply/')
        self.assertContains(response, self.NOT_ALREADY_MEMBER_TEXT)
        self.assertNotContains(response, self.ALREADY_MEMBER_TEXT)

    def test_incomplete_applications_are_rejected(self):
        self.login_as_non_member()
        response = self.client.post('/accounts/apply/', {})
        self.assertContains(response, self.APP_REJECTED_TEXT)
        self.assertContains(response, self.APP_REJECTED_FIELD_TEXT)
        self.assertNotContains(response, self.APP_SENT_TEXT)

    def apply(self):
        self.login_as_non_member()
        self.non_member.first_name = 'Bob'
        self.non_member.last_name = 'Jones'
        self.non_member.email = 'bob@example.org'
        self.non_member.save()

        data = {'city': str(self.wnyc.city.id), 'info': 'sup'}
        response = self.client.post('/accounts/apply/', data, follow=True)
        self.assertRedirects(response, '/')
        self.assertNotContains(response, self.APP_REJECTED_TEXT)
        self.assertNotContains(response, self.APP_REJECTED_FIELD_TEXT)
        self.assertContains(response, self.APP_SENT_TEXT)

        for email in mail.outbox:
            self.assertEqual(email.subject,
                             'non_member (Hive NYC) has applied for full '
                             'access to the Hive directory!')
            for regexp in [r'Bob Jones', r'bob@example\.org']:
                self.assertRegexpMatches(email.body, regexp)

    def test_applying_with_no_city_staff_sends_email_to_superusers(self):
        create_user('root', email='root@example.org', is_superuser=True)

        self.apply()

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['root@example.org'])
        self.assertRegexpMatches(mail.outbox[0].body, self.NO_STAFF_TEXT)

    def test_applying_sends_email_to_selected_city_staff(self):
        self.wnyc_member.is_staff = True
        self.wnyc_member.save()

        self.apply()

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['member@wnyc.org'])
        self.assertNotRegexpMatches(mail.outbox[0].body, self.NO_STAFF_TEXT)
