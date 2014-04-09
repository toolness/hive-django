import doctest
import unittest
from django.core.exceptions import ValidationError

from directory import phonenumber
from directory.phonenumber import validate_phone_number

def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(phonenumber))
    return tests

class PhoneNumberTests(unittest.TestCase):
    def test_phone_number_field_instantiates(self):
        phonenumber.PhoneNumberField()

    def test_validate_phone_number_rejects_invalid_numbers(self):
        self.assertRaises(ValidationError, validate_phone_number, '$')

    def test_validate_twitter_name_accepts_valid_numbers(self):
        validate_phone_number('123-456-7890')
