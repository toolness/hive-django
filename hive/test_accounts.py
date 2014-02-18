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
