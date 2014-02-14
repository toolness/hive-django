import os
from django.test import TestCase
from mock import patch

import settings

class Tests(TestCase):
    def test_set_default_env_sets_default_values(self):
        with patch.dict(os.environ, {'TEST_FOO': ''}):
            del os.environ['TEST_FOO']
            settings.set_default_env(TEST_FOO='bar')
            self.assertEqual(os.environ['TEST_FOO'], 'bar')

    def test_set_default_env_does_not_overwrite_existing_values(self):
        with patch.dict(os.environ, {'TEST_FOO': ''}):
            settings.set_default_env(TEST_FOO='bar')
            self.assertEqual(os.environ['TEST_FOO'], '')

    def test_set_default_db_follows_env_vars(self):
        with patch.dict(os.environ, {'DATABASE_URL': 'FOO', 'FOO': 'bar'}):
            settings.set_default_db('meh')
            self.assertEqual(os.environ['DATABASE_URL'], 'bar')

    def test_set_default_db_does_not_overwrite_existing_value(self):
        with patch.dict(os.environ, {'DATABASE_URL': 'foo'}):
            settings.set_default_db('meh')
            self.assertEqual(os.environ['DATABASE_URL'], 'foo')

    def test_set_default_db_sets_default_value(self):
        with patch.dict(os.environ, {'DATABASE_URL': ''}):
            del os.environ['DATABASE_URL']
            settings.set_default_db('meh')
            self.assertEqual(os.environ['DATABASE_URL'], 'meh')
