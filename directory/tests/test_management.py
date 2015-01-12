import StringIO
import os
from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth.models import Group

ROOT = os.path.abspath(os.path.dirname(__file__))
path = lambda *x: os.path.join(ROOT, *x)

class ManagementCommandTests(TestCase):
    def test_seeddata_works_with_password(self):
        output = StringIO.StringIO()
        call_command('seeddata', password="LOL", stdout=output)
        self.assertRegexpMatches(output.getvalue(), "password 'LOL'")

    def test_seeddata_works_with_no_options(self):
        output = StringIO.StringIO()
        call_command('seeddata', stdout=output)
        self.assertRegexpMatches(output.getvalue(), "password 'test'")

    def test_initgroups_works(self):
        call_command('initgroups', stdout=StringIO.StringIO())
        Group.objects.get(name='City Editors')
        Group.objects.get(name='Multi-City Editors')

class ImportOrgsTests(TestCase):
    fixtures = ['wnyc.json']

    def test_importorgs_works(self):
        output = StringIO.StringIO()
        errors = StringIO.StringIO()
        call_command(
            'importorgs',
            path('test_management_importorgs.csv'),
            city='nyc',
            stdout=output,
            stderr=errors
        )
        self.assertEqual(
            output.getvalue(),
            "Importing American Museum of Natural History...\n"
        )
        self.assertRegexpMatches(
            errors.getvalue(),
            "WARNING: cannot parse contact: u'Lisa Doe"
        )
