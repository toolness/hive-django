import os
from django.test import TestCase
from mock import patch

from .settings_utils import set_default_env, set_default_db

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
