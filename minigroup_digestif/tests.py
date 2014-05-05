from django.test import TestCase, Client
from django.test.utils import override_settings

def userpass(string):
    return 'Basic %s' % (string.encode('base64'))

class BaseTestCase(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.client = Client(enforce_csrf_checks=True)

@override_settings(MINIGROUP_DIGESTIF_USERPASS='')
class DisabledEndpointTests(BaseTestCase):
    def test_return_not_implemented_if_unconfigured(self):        
        response = self.client.post('/minigroup_digestif/send')
        self.assertEqual(response.status_code, 501)

@override_settings(MINIGROUP_DIGESTIF_USERPASS='user:pass')
class EnabledEndpointTests(BaseTestCase):
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

    def test_valid_userpass_with_html_returns_200(self):
        response = self.client.post(
            '/minigroup_digestif/send',
            {'html': '<p>hello!</p>'},
            HTTP_AUTHORIZATION=userpass('user:pass')
        )
        self.assertEqual(response.status_code, 200)
