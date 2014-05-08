from django.core import mail
from django.test import TestCase, Client
from django.test.utils import override_settings
from django.contrib.auth.models import User

from directory.models import Membership

def userpass(string):
    return 'Basic %s' % (string.encode('base64'))

@override_settings(MINIGROUP_DIGESTIF_USERPASS='user:pass')
class EndpointTests(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.client = Client(enforce_csrf_checks=True)

    def test_no_authorization_header_returns_401(self):
        response = self.client.post('/minigroup_digestif/send')
        self.assertEqual(response.status_code, 401)

    def test_malformed_authorization_header_returns_401(self):
        response = self.client.post('/minigroup_digestif/send',
                                    HTTP_AUTHORIZATION='lol')
        self.assertEqual(response.status_code, 401)

    def test_non_basic_auth_returns_401(self):
        response = self.client.post('/minigroup_digestif/send',
                                    HTTP_AUTHORIZATION='Digest lol')
        self.assertEqual(response.status_code, 401)

    def test_non_base64_userpass_returns_401(self):
        response = self.client.post('/minigroup_digestif/send',
                                    HTTP_AUTHORIZATION='Basic lol')
        self.assertEqual(response.status_code, 401)

    def test_invalid_userpass_returns_401(self):
        response = self.client.post('/minigroup_digestif/send',
                                    HTTP_AUTHORIZATION=userpass('a:b'))
        self.assertEqual(response.status_code, 401)

    def test_valid_userpass_without_html_returns_400(self):
        response = self.client.post(
            '/minigroup_digestif/send',
            HTTP_AUTHORIZATION=userpass('user:pass')
        )
        self.assertEqual(response.status_code, 400)

    @override_settings(ORIGIN='http://example.org')
    def test_valid_userpass_with_html_returns_200(self):
        # This user doesn't subscribe to the digest.
        user = User(username='joe', email='joe@example.com')
        user.save()

        # This user subscribes to the digest, but has no email.
        user = User(username='ann')
        user.save()
        user.membership.receives_minigroup_digest = True
        user.membership.save()

        # This user subscribes to the digest.
        user = User(username='bob', email='bob@example.com')
        user.save()
        user.membership.receives_minigroup_digest = True
        user.membership.save()

        response = self.client.post(
            '/minigroup_digestif/send',
            {'html': '<p>hello!</p>'},
            HTTP_AUTHORIZATION=userpass('user:pass')
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)

        msg = mail.outbox[0]
        self.assertEqual(msg.to, [])
        self.assertEqual(msg.bcc, ['bob@example.com'])
        self.assertEqual(
            msg.body,
            u'<p>hello!</p>'
            '<p><small>To unsubscribe from this digest, '
            'please visit your '
            '<a href="http://example.org/accounts/profile/">'
            'account settings</a>.</small></p>'
        )
        self.assertEqual(msg.content_subtype, 'html')
