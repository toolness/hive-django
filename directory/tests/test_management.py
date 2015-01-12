import StringIO
from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth.models import Group

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
