from django.test import TestCase
from django.core.exceptions import ValidationError

from ..twitter import validate_twitter_name

class TwitterNameTests(TestCase):
    def test_validate_twitter_name_rejects_invalid_names(self):
        self.assertRaises(ValidationError, validate_twitter_name, '$')
        self.assertRaises(ValidationError, validate_twitter_name,
                          'reallyreallyreallyreallylongusername')

    def test_validate_twitter_name_accepts_valid_names(self):
        validate_twitter_name('toolness')
        validate_twitter_name('t')
        validate_twitter_name('super_burger')
        validate_twitter_name('blargy23')
