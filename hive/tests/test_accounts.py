import re
from mock import patch
from django.contrib.auth.models import User
from django.conf import settings
from django.core import mail
from django.test import TestCase
from django.test.client import Client

class AccountTests(TestCase):
    def assertPathExists(self, path, status_code=200):
        c = Client()
        response = c.get(path)
        msg = 'GET %s should return %d (actual %d)' % (
            path,
            status_code,
            response.status_code
        )
        self.assertEqual(response.status_code, status_code, msg)

    def test_password_change_paths(self):
        self.assertPathExists('/accounts/password/change/', 302)
        self.assertPathExists('/accounts/password/change/done/', 302)

    def test_password_reset_paths(self):
        self.assertPathExists('/accounts/password/reset/')
        self.assertPathExists('/accounts/password/reset/confirm/abc-lol/')
        self.assertPathExists('/accounts/password/reset/complete/')
        self.assertPathExists('/accounts/password/reset/done/')

    def test_login_paths(self):
        self.assertPathExists('/accounts/login/')
        self.assertPathExists('/accounts/logout/')

    def test_activation_paths(self):
        self.assertPathExists('/accounts/activate/blarg/')
        self.assertPathExists('/accounts/activate/complete/')

    def test_registration_paths(self):
        self.assertPathExists('/accounts/register/')
        self.assertPathExists('/accounts/register/complete/')

    @patch.dict(settings.__dict__, {'ORIGIN': 'http://me.org'})
    def test_registration_works(self):
        c = Client()
        response = c.post('/accounts/register/', {
            'username': 'foo',
            'email': 'foo@example.org',
            'password1': 'lol',
            'password2': 'lol',
        })
        self.assertRedirects(response, '/accounts/register/complete/')
        self.assertEqual(len(mail.outbox), 1)

        msg = mail.outbox[0]
        self.assertEqual(msg.to, ['foo@example.org'])
        self.assertRegexpMatches(msg.body,
                                 r'http://me\.org/accounts/activate/')
        key = re.search(r'/activate/([0-9a-f]+)/', msg.body).group(1)

        self.assertFalse(User.objects.get(username='foo').is_active)

        response = c.get('/accounts/activate/%s/' % key)
        self.assertRedirects(response, '/accounts/activate/complete/')

        self.assertTrue(User.objects.get(username='foo').is_active)

class AccountSwitchingTests(TestCase):
    def setUp(self):
        super(AccountSwitchingTests, self).setUp()
        self.admin = User.objects.create_superuser(
            'admin', 'admin@example.org', 'lol'
        )
        self.staff = User.objects.create_user(
            'staff', 'staff@example.org', 'lol'
        )
        self.staff.is_staff = True
        self.staff.save()
        self.joe = User.objects.create_user(
            'joe', 'joe@example.org', 'lol'
        )

    def post(self, path, username=None):
        c = Client()
        if username is not None: c.login(username=username, password='lol')
        response = c.post(path, follow=True)
        return c, response

    def assertRedirectsToLogin(self, path, username=None):
        c, response = self.post(path, username)
        self.assertRedirects(response, '/accounts/login/?next=%s' % path)

    def test_switching_anonymously_redirects_to_login(self):
        self.assertRedirectsToLogin('/admin/switch-user/joe')

    def test_switching_as_normal_user_is_denied(self):
        self.assertRedirectsToLogin('/admin/switch-user/admin', 'joe')

    def test_switching_as_staff_is_denied(self):
        self.assertRedirectsToLogin('/admin/switch-user/admin', 'staff')

    def test_switching_as_superuser_works(self):
        c, response = self.post('/admin/switch-user/joe', 'admin')
        self.assertRedirects(response, '/')
        self.assertEqual(response.context['user'].username, 'joe')

    def test_switching_back_to_superuser_works(self):
        c, response = self.post('/admin/switch-user/joe', 'admin')
        self.assertEqual(response.context['user'].username, 'joe')

        response = c.post('/admin/switch-user-back', follow=True)
        self.assertRedirects(response, '/')
        self.assertEqual(response.context['user'].username, 'admin')

    def test_get_method_is_not_allowed(self):
        c = Client()
        c.login(username='admin', password='lol')

        self.assertEqual(c.get('/admin/switch-user/joe').status_code, 405)
        self.assertEqual(c.get('/admin/switch-user-back').status_code, 405)
