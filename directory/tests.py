from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import Organization, validate_twitter_name

class OrganizationTests(TestCase):
    fixtures = ['radio-rookies.json']

    def test_org_has_memberships(self):
        org = Organization.objects.get(pk=1)
        self.assertEqual(org.memberships.count(), 0)
        user = User(username='foo')
        user.save()
        user.membership.organization = org
        user.membership.save()
        self.assertEqual(org.memberships.count(), 1)

class MembershipTests(TestCase):
    def test_user_membership_is_created_on_save(self):
        user = User(username='foo')
        user.save()
        self.assertTrue(user.membership)
        self.assertTrue(user.membership.is_listed)
        self.assertFalse(user.membership.organization)

class TwitterNameTests(TestCase):
    def test_validate_twitter_name_rejects_invalid_names(self):
        self.assertRaises(ValidationError, validate_twitter_name, '$')
        self.assertRaises(ValidationError, validate_twitter_name,
                          'reallyreallyreallyreallylongusername')

    def test_validate_twitter_name_accepts_valid_names(self):
        validate_twitter_name('toolness')
        validate_twitter_name('t')
        validate_twitter_name('super_burger')
