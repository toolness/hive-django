import re
from mock import patch
from django.contrib.auth.models import User
from django.conf import settings
from django.core import mail
from django.test import TestCase
from django.test.client import Client

class AccountUrlTests(TestCase):
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

    def test_registration_enforces_unique_email(self):
        User(username='foo', email='foo@example.org').save()
        c = Client()
        response = c.post('/accounts/register/', {
            'username': 'bar',
            'email': 'foo@example.org',
            'password1': 'lol',
            'password2': 'lol',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'email address is already in use')
        self.assertContains(response, 'password reset')

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
