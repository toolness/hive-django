import os
import doctest
import unittest
import StringIO
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.management import call_command

from directory.management.commands import importorgs
from directory.models import Organization, \
                             MembershipRole, OrganizationMembershipType
from .test_views import WnycTestCase

ROOT = os.path.abspath(os.path.dirname(__file__))
path = lambda *x: os.path.join(ROOT, *x)

def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(importorgs))
    return tests

class UnitTests(unittest.TestCase):
    def test_parse_contact(self):
        pc = importorgs.parse_contact
        text = ('Foo Bar\nCool Person\nfoo@bar.org\n'
                'tags: super awesome, o yea')
        self.assertEqual(pc(text), dict(
            full_name='Foo Bar',
            first_name='Foo',
            last_name='Bar',
            title='Cool Person',
            email='foo@bar.org',
            tags=['super awesome', 'o yea'],
        ))

class ImportOrgsTests(WnycTestCase):
    def test_importorgs_works(self):
        orgtype = OrganizationMembershipType(
            name='Ultra Org',
            city=self.wnyc.city
        )
        orgtype.save()

        role = MembershipRole(name='Awesome Person', city=self.wnyc.city)
        role.save()

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

        org = Organization.objects.get(
            slug='american-museum-of-natural-history'
        )
        self.assertEqual(list(org.membership_types.all()), [orgtype])

        john = User.objects.get(username='johndoe')
        self.assertEqual(
            list(john.membership.roles.all()),
            [role]
        )
