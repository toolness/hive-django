from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .twitter import TwitterNameField

def is_user_hive_member(user, organization=None):
    if not (user.is_active and user.membership.organization):
        return False
    if organization is None: return True
    return organization == user.membership.organization

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
    twitter_name = TwitterNameField(
        help_text="The twitter account for the organization.",
        blank=True,
    )
    hive_member_since = models.DateField(
        help_text="The date the organization joined the Hive network."
    )
    mission = models.TextField(
        help_text="The organization's mission and philosophy."
    )

    def __unicode__(self):
        return self.name

    def membership_directory(self):
        return self.memberships.filter(is_listed=True)

    # TODO: How to represent youth audience?

    # TODO: How to represent different content channels? e.g.,
    # youtube, blog, flickr, instagram, etc?

class Membership(models.Model):
    '''
    Represents a person who is a member of an organization.
    '''

    user = models.OneToOneField(User)
    organization = models.ForeignKey(Organization, blank=True, null=True,
                                     related_name='memberships')
    title = models.CharField(
        help_text="The person's title at their organization.",
        max_length=100,
        blank=True
    )
    is_listed = models.BooleanField(
        default=True,
        help_text="Whether the person is listed under their organization in "
                  "the Hive member directory."
    )

@receiver(post_save, sender=User)
def create_membership_for_user(sender, raw, instance, **kwargs):
    if raw: return
    if not len(Membership.objects.filter(user=instance)):
        membership = Membership(user=instance)
        membership.save()
