import re
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

MAX_TWITTER_NAME_LEN = 15

def validate_twitter_name(value):
    base_err = '"%s" is not a valid Twitter username.' % value
    if len(value) > MAX_TWITTER_NAME_LEN:
        raise ValidationError(base_err + ' A username cannot be longer than '
                              '%d characters.' % MAX_TWITTER_NAME_LEN)
    if not re.match('^[A-Za-z_]+$', value):
        raise ValidationError(
            base_err +
            ' A username can only contain alphanumeric characters (letters '
            'A-Z, numbers 0-9) with the exception of underscores.'
        )

class Organization(models.Model):
    '''
    Represents a Hive member organization.
    '''

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
        max_length=MAX_TWITTER_NAME_LEN,
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

class OrganizationMembership(models.Model):
    '''
    Represents a person who is a member of an organization.
    '''

    user = models.OneToOneField(User, related_name='membership')
    organization = models.ForeignKey(Organization, blank=True, null=True)
    is_listed = models.BooleanField(
        default=True,
        help_text="Whether the person is listed under their organization in "
                  "the Hive member directory."
    )

@receiver(post_save, sender=User)
def create_membership_for_user(sender, raw, instance, **kwargs):
    if raw: return
    if not len(OrganizationMembership.objects.filter(user=instance)):
        membership = OrganizationMembership(user=instance)
        membership.save()
