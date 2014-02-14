import os
from django.test import TestCase

import settings

class Tests(TestCase):
    def test_set_default_env_sets_default_values(self):
        if 'TEST_FOO' in os.environ: del os.environ['TEST_FOO']
        settings.set_default_env(TEST_FOO='bar')
        self.assertEqual(os.environ['TEST_FOO'], 'bar')
        del os.environ['TEST_FOO']

    def test_set_default_env_does_not_overwrite_existing_values(self):
        os.environ['TEST_FOO'] = ''
        settings.set_default_env(TEST_FOO='bar')
        self.assertEqual(os.environ['TEST_FOO'], '')
        del os.environ['TEST_FOO']
