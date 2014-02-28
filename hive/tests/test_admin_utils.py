from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User

class UserSwitchingTests(TestCase):
    def setUp(self):
        super(UserSwitchingTests, self).setUp()
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
