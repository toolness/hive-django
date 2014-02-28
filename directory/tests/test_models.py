from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from ..models import Organization, ContentChannel
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

    def test_min_age_greater_than_max_raises_validation_error(self):
        wnyc = Organization.objects.get(slug='wnyc')
        wnyc.full_clean()
        wnyc.min_youth_audience_age = 99
        wnyc.max_youth_audience_age = 1
        self.assertRaisesRegexp(
            ValidationError,
            "Minimum youth audience age may not be greater than maximum",
            wnyc.full_clean
        )

class ContentChannelTests(TestCase):
    def test_fa_icon_returns_empty_string_if_none_available(self):
        c = ContentChannel(category='other')
        self.assertEqual(c.fa_icon, '')

    def test_fa_icon_returns_css_class_name_if_available(self):
        c = ContentChannel(category='flickr')
        self.assertEqual(c.fa_icon, 'fa-flickr')

    def test_display_name_is_category_when_category_is_not_other(self):
        c = ContentChannel(category='flickr')
        self.assertEqual(c.display_name, 'Flickr')

    def test_display_name_is_other_when_category_is_other(self):
        c = ContentChannel(category='other')
        self.assertEqual(c.display_name, 'Other')

    def test_display_name_is_name_when_category_is_other(self):
        c = ContentChannel(category='other', name='Foo')
        self.assertEqual(c.display_name, 'Foo')
