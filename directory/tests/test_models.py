from django.test import TestCase
from django.contrib.auth.models import User

from ..models import Organization
from ..management.commands.seeddata import create_user

class MembershipTests(TestCase):
    def test_user_membership_is_created_on_save(self):
        user = User(username='foo')
        user.save()
        self.assertTrue(user.membership)
        self.assertTrue(user.membership.is_listed)
        self.assertFalse(user.membership.organization)

class OrganizationTests(TestCase):
    fixtures = ['wnyc.json']

    def setUp(self):
        super(OrganizationTests, self).setUp()
        self.wnyc = Organization.objects.get(pk=1)

    def test_org_has_memberships(self):
        self.assertEqual(self.wnyc.memberships.count(), 0)
        create_user('foo', organization=self.wnyc)
        self.assertEqual(self.wnyc.memberships.count(), 1)
