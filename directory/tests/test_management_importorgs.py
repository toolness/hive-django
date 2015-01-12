import os
import doctest
import unittest
import StringIO
from django.test import TestCase
from django.core.management import call_command

from directory.management.commands import importorgs

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
