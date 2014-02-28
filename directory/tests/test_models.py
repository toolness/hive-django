from django.test import TestCase
from django.contrib.auth.models import User

class MembershipTests(TestCase):
    def test_user_membership_is_created_on_save(self):
        user = User(username='foo')
        user.save()
        self.assertTrue(user.membership)
        self.assertTrue(user.membership.is_listed)
        self.assertFalse(user.membership.organization)
