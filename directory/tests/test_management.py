import StringIO
from mock import patch
from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth.models import Group

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
