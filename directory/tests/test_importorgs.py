import doctest
import unittest

from directory.management.commands import importorgs

def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(importorgs))
    return tests

class ImportOrgsTests(unittest.TestCase):
    def test_parse_contact(self):
        pc = importorgs.parse_contact
        self.assertEqual(pc('Foo Bar\nCool Person\nfoo@bar.org'), dict(
            first_name='Foo',
            last_name='Bar',
            title='Cool Person',
            email='foo@bar.org'
        ))
