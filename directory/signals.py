from django.dispatch import receiver
from django.contrib.sites.models import Site
from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in
from django.contrib import messages
from registration.signals import user_activated

from .models import City, User, Organization, Membership, is_user_vouched_for

@receiver(post_save, sender=City)
def clear_site_cache_when_city_changes(**kwargs):
    # It's possible that the site may be associated with a different
    # city now, so clear the site cache.
    Site.objects.clear_cache()

@receiver(post_save, sender=User)
def create_membership_for_user(sender, raw, instance, **kwargs):
    if raw: return
    if not len(Membership.objects.filter(user=instance)):
        membership = Membership(user=instance)
        membership.save()

@receiver(user_activated)
def auto_register_user_with_organization(sender, user, request, **kwargs):
    if user.membership.organization: return
    orgs = Organization.objects.possible_affiliations_for(user)
    if orgs.count() != 1: return
    org = orgs[0]
    user.membership.organization = org
    user.membership.save()

@receiver(user_logged_in)
def tell_user_to_update_their_profile(sender, user, request, **kwargs):
    if not is_user_vouched_for(user): return
    if not user.membership.bio:
        messages.info(request,
                      'You don\'t have a bio! You should write one '
                      'so community members can learn more about you. '
                      'Just visit your user profile by accessing the '
                      'user menu at the top-right corner of this page.',
                      fail_silently=True)
