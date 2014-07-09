from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

from .test_views import WnycTestCase
from .test_multi_city import using_multi_city_site
from ..models import Organization, ContentChannel, Expertise, City, \
                     Membership
from ..management.commands.seeddata import create_user

class MembershipTests(TestCase):
    fixtures = ['wnyc.json']

    def test_user_membership_is_created_on_save(self):
        user = User(username='foo')
        user.save()
        self.assertTrue(user.membership)
        self.assertTrue(user.membership.is_listed)
        self.assertFalse(user.membership.organization)

    def test_city_is_none_when_org_is_none(self):
        m = Membership()
        self.assertEqual(m.city, None)

    def test_city_is_org_city(self):
        m = Membership(organization=Organization.objects.get(slug='wnyc'))
        self.assertEqual(m.city.short_name, 'NYC')

class ExpertiseTests(WnycTestCase):
    def test_manager_of_vouched_users_works(self):
        Expertise(category='other', user=self.wnyc_member).save()
        Expertise(category='other', user=self.non_member).save()
        skills = Expertise.objects.of_vouched_users()

        self.assertEqual(len(skills), 1)
        self.assertEqual(skills[0], self.wnyc_member.skills.all()[0])

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

class ContentChannelManagerTests(WnycTestCase):
    def assertCats(self, channels, cats):
        self.assertEqual([channel.category for channel in channels], cats)

    def test_unique_with_icons_excludes_other_category(self):
        ContentChannel(category='other', url='http://wnyc.org/',
                       organization=self.wnyc).save()
        self.assertCats(self.wnyc.content_channels.unique_with_icons(),
                        ['facebook'])

    def test_unique_with_icons(self):
        ContentChannel(category='facebook', url='http://facebook.com/a',
                       organization=self.wnyc).save()
        self.assertCats(self.wnyc.content_channels.unique_with_icons(),
                        ['facebook'])

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

class CityTests(TestCase):
    def test_shortest_name_uses_short_name_if_available(self):
        self.assertEqual(City(name='New York City',
                              short_name='NYC').shortest_name, 'NYC')

    def test_shortest_name_falls_back_to_name(self):
        self.assertEqual(City(name='Chicago').shortest_name, 'Chicago')

class CityShouldBeMentionedTests(TestCase):
    @using_multi_city_site
    def test_always_returns_true_when_multi_city(self):
        city = City.objects.get(pk=1)
        self.assertTrue(city.should_be_mentioned())

    def test_returns_false_when_city_is_same_as_site(self):
        city = City.objects.get(pk=1)
        self.assertFalse(city.should_be_mentioned())

    def test_returns_true_when_city_is_different_from_site(self):
        city = City()
        self.assertTrue(city.should_be_mentioned())
