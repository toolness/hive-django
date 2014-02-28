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

    def test_org_has_memberships(self):
        wnyc = Organization.objects.get(slug='wnyc')
        self.assertEqual(wnyc.memberships.count(), 0)
        create_user('foo', organization=wnyc)
        self.assertEqual(wnyc.memberships.count(), 1)
