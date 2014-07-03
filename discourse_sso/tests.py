import urlparse
from django.test.utils import override_settings

from directory.tests.test_views import WnycTestCase
from .views import pack_and_sign_payload, unpack_and_verify_payload

@override_settings(DISCOURSE_SSO_SECRET='test',
                   DISCOURSE_SSO_ORIGIN='http://discourse.org')
class EndpointTests(WnycTestCase):
    def test_non_members_are_redirected_to_login(self):
        self.assertNonMembersAreDenied('/discourse_sso/')

    def test_invalid_payloads_are_rejected(self):
        self.login_as_wnyc_member()
        payload = pack_and_sign_payload({'nonce': '1'}, secret='INVALID')
        response = self.client.get('/discourse_sso/', payload)

        self.assertEqual(response.status_code, 400)

    def test_members_are_redirected_to_discourse(self):
        self.login_as_wnyc_member()
        payload = pack_and_sign_payload({'nonce': '1'})
        response = self.client.get('/discourse_sso/', payload)

        self.assertEqual(response.status_code, 302)

        loc = urlparse.urlparse(response['location'])
        self.assertEqual(loc.scheme, 'http')
        self.assertEqual(loc.netloc, 'discourse.org')
        self.assertEqual(loc.path, '/session/sso_login')

        query_dict = dict(urlparse.parse_qsl(loc.query))
        self.assertEqual(unpack_and_verify_payload(query_dict), {
            'email': 'member@wnyc.org',
            'external_id': '2',
            'name': 'Brian Lehrer (WNYC\'s Radio Rookies)',
            'nonce': '1',
            'username': 'wnyc_member'
        })
