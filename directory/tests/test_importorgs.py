import unittest
import doctest

from directory.management.commands import importorgs

def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(importorgs))
    return tests
