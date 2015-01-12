import StringIO
import os
from mock import patch
from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth.models import Group

ROOT = os.path.abspath(os.path.dirname(__file__))
path = lambda *x: os.path.join(ROOT, *x)

class ManagementCommandTests(TestCase):
    def test_seeddata_works_with_password(self):
        output = StringIO.StringIO()
        with patch('sys.stdout', output):
            call_command('seeddata', password="LOL")
        self.assertRegexpMatches(output.getvalue(), "password 'LOL'")

    def test_seeddata_works_with_no_options(self):
        output = StringIO.StringIO()
        with patch('sys.stdout', output): call_command('seeddata')
        self.assertRegexpMatches(output.getvalue(), "password 'test'")

    def test_initgroups_works(self):
        output = StringIO.StringIO()
        with patch('sys.stdout', output): call_command('initgroups')
        Group.objects.get(name='City Editors')
        Group.objects.get(name='Multi-City Editors')

class ImportOrgsTests(TestCase):
    fixtures = ['wnyc.json']

    def test_importorgs_works(self):
        output = StringIO.StringIO()
        errors = StringIO.StringIO()
        with patch('sys.stdout', output):
            with patch('sys.stderr', errors):
                call_command(
                    'importorgs',
                    path('test_management_importorgs.csv'),
                    city='nyc'
                )
        self.assertEqual(
            output.getvalue(),
            "Importing American Museum of Natural History...\n"
        )
        self.assertRegexpMatches(
            errors.getvalue(),
            "WARNING: cannot parse contact: u'Lisa Doe"
        )
