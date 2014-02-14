import os
from django.test import TestCase
from mock import patch

from .settings_utils import set_default_env, set_default_db, \
                            parse_email_backend_url

class SettingsUtilsTests(TestCase):
    def test_set_default_env_sets_default_values(self):
        with patch.dict(os.environ, {'TEST_FOO': ''}):
            del os.environ['TEST_FOO']
            set_default_env(TEST_FOO='bar')
            self.assertEqual(os.environ['TEST_FOO'], 'bar')

    def test_set_default_env_does_not_overwrite_existing_values(self):
        with patch.dict(os.environ, {'TEST_FOO': ''}):
            set_default_env(TEST_FOO='bar')
            self.assertEqual(os.environ['TEST_FOO'], '')

    def test_set_default_db_follows_env_vars(self):
        with patch.dict(os.environ, {'DATABASE_URL': 'FOO', 'FOO': 'bar'}):
            set_default_db('meh')
            self.assertEqual(os.environ['DATABASE_URL'], 'bar')

    def test_set_default_db_does_not_overwrite_existing_value(self):
        with patch.dict(os.environ, {'DATABASE_URL': 'foo'}):
            set_default_db('meh')
            self.assertEqual(os.environ['DATABASE_URL'], 'foo')

    def test_set_default_db_sets_default_value(self):
        with patch.dict(os.environ, {'DATABASE_URL': ''}):
            del os.environ['DATABASE_URL']
            set_default_db('meh')
            self.assertEqual(os.environ['DATABASE_URL'], 'meh')

    def test_parse_email_backend_url_accepts_console(self):
        self.assertEqual(parse_email_backend_url('console:'), {
            'EMAIL_BACKEND': 'django.core.mail.backends.console.EmailBackend'
        })

    def test_parse_email_backend_url_accepts_smtp_without_auth(self):
        self.assertEqual(parse_email_backend_url('smtp://foo.org:25'), {
            'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
            'EMAIL_HOST': 'foo.org',
            'EMAIL_PORT': 25
        })

    def test_parse_email_backend_url_accepts_smtp_with_auth(self):
        self.assertEqual(parse_email_backend_url('smtp://a:b@foo.org:25'), {
            'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
            'EMAIL_HOST': 'foo.org',
            'EMAIL_PORT': 25,
            'EMAIL_HOST_USER': 'a',
            'EMAIL_HOST_PASSWORD': 'b'
        })

    def test_parse_email_backend_url_accepts_smtp_plus_tls(self):
        self.assertEqual(parse_email_backend_url('smtp+tls://foo.org:25'), {
            'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
            'EMAIL_USE_TLS': True,
            'EMAIL_HOST': 'foo.org',
            'EMAIL_PORT': 25
        })
