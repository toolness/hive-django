import re
from django.db import models
from django.core.exceptions import ValidationError

def validate_twitter_name(value):
    base_err = '"%s" is not a valid Twitter name.' % value
    if len(value) > 15:
        raise ValidationError(base_err + ' A username cannot be longer than '
                              '15 characters.')
    if not re.match('^[A-Za-z_]+$', value):
        raise ValidationError(
            base_err +
            ' A username can only contain alphanumeric characters (letters '
            'A-Z, numbers 0-9) with the exception of underscores.'
        )

class Organization(models.Model):
    name = models.CharField(
        help_text="The full name of the organization.",
        max_length=100
    )
    website = models.URLField(
        help_text="The URL of the organization's primary website."
    )
    address = models.TextField(
        help_text="The full address of the organization's main office."
    )
    twitter_name = models.CharField(
        max_length=15,
        help_text="The twitter account for the organization.",
        blank=True,
        validators=[validate_twitter_name]
    )
    hive_member_since = models.DateField(
        help_text="The date the organization joined the Hive network."
    )
    mission = models.TextField(
        help_text="The organization's mission and philosophy."
    )

    # TODO: How to represent youth audience?

    # TODO: How to represent different content channels? e.g.,
    # youtube, blog, flickr, instagram, etc?
