from django.test import TestCase

from .models import Organization

class DirectoryTests(TestCase):
    def test_organization_does_not_explode(self):
        o = Organization()
