from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver
from registration.signals import user_activated

from .twitter import TwitterNameField
from .phonenumber import PhoneNumberField

def is_user_vouched_for(user, organization=None):
    '''
    Returns whether the given user belongs to a Hive-affiliated
    organization. If an organization is supplied, returns
    whether the user belongs to that organization specifically.
    '''

    if not (user.is_active and user.membership.organization
            and user.membership.organization.is_active):
        return False
    if organization is None: return True
    return organization == user.membership.organization

def is_user_privileged(user):
    '''
    Returns whether the given user can view personally identifiable
    information, phone numbers, and so forth.
    '''

    return is_user_vouched_for(user) or (user.is_active and user.is_staff)

def get_current_city(request=None):
    '''
    Returns the City for the current Site. If the current Site is
    multi-city, then None is returned.
    '''

    try:
        return get_current_site(request).city
    except City.DoesNotExist:
        return None

class City(models.Model):
    '''
    Represents a city that a Hive network exists in.
    '''

    HIVE_TYPE_CHOICES = (
        ('emerging', 'Emerging'),
        ('community', 'Community'),
        ('network', 'Network'),
    )

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    site = models.OneToOneField(
        Site,
        help_text="The site associated with this city. If blank, this "
                  "city's directory will only be accessible on multi-city "
                  "sites.",
        null=True, blank=True
    )
    name = models.CharField(
        help_text="The full name of the city (e.g., New York City).",
        max_length=100
    )
    short_name = models.CharField(
        help_text="The short/abbreviated name of the city (e.g., NYC).",
        max_length=20,
        blank=True
    )
    slug = models.SlugField(
        help_text="A short identifier for the city, used in "
                  "URLs and such. Only letters, numbers, underscores, and "
                  "hyphens are allowed.",
        unique=True
    )
    hive_type = models.CharField(
        help_text="The type of Hive in this city.",
        choices=HIVE_TYPE_CHOICES,
        default='emerging',
        max_length=25,
    )

    @property
    def shortest_name(self):
        return self.short_name or self.name

    def should_be_mentioned(self, request=None):
        '''
        Given the current Site context, returns whether or not the city 
        should be mentioned by name.

        If the current Site is multi-city, then we always want to
        mention the name of a city, as it's never assumed to be a 
        particular default.

        Otherwise, we only want to mention the name of a city if it's
        different from the one that the current Site is associated with.
        '''

        current_city = get_current_city(request)
        if current_city is None:
            return True
        return current_city != self

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'cities'
        ordering = ['name']

class OrganizationMembershipType(models.Model):
    '''
    Represents a type of organization membership. This can be
    anything specific to a particular Hive, e.g. "partner", "affiliate",
    "community", or something else.
    '''

    name = models.CharField(
        help_text="The name of the organization membership type.",
        max_length=50
    )
    description = models.TextField(
        help_text="Description of the organization membership type."
    )
    city = models.ForeignKey(
        City,
        help_text="The Hive city that the membership type pertains to."
    )

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Organization(models.Model):
    '''
    Represents a Hive organization.
    '''

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    city = models.ForeignKey(
        City,
        help_text="The city to which the organization belongs."
    )
    name = models.CharField(
        help_text="The full name of the organization.",
        max_length=100
    )
    slug = models.SlugField(
        help_text="A short identifier for the organization, used in "
                  "URLs and such. Only letters, numbers, underscores, and "
                  "hyphens are allowed.",
        unique=True
    )
    website = models.URLField(
        help_text="The URL of the organization's primary website."
    )
    email_domain = models.CharField(
        help_text="The domain which members of this organization have "
                  "email addresses at.",
        blank=True,
        max_length=50
    )
    address = models.TextField(
        help_text="The full address of the organization's main office.",
        blank=True,
    )
    twitter_name = TwitterNameField(
        help_text="The twitter account for the organization.",
        blank=True,
    )
    hive_member_since = models.DateField(
        help_text="The date the organization joined the Hive network. "
                  "Only the month and year will be used.",
        null=True,
        blank=True
    )
    mission = models.TextField(
        help_text="The organization's mission and philosophy. Markdown "
                  "and basic HTML tags are allowed.",
        blank=True,
    )
    min_youth_audience_age = models.SmallIntegerField(
        help_text="Minimum age of youth, in years, that the organization's "
                  "programs target.",
        validators=[MinValueValidator(0)],
        default=0
    )
    max_youth_audience_age = models.SmallIntegerField(
        help_text="Maximum age of youth, in years, that the organization's "
                  "programs target.",
        validators=[MinValueValidator(0)],
        default=18
    )
    is_active = models.BooleanField(
        help_text="Designates whether this organization should be treated "
                  "as active. Unselect this instead of deleting "
                  "organizations.",
        default=True
    )
    membership_types = models.ManyToManyField(
        OrganizationMembershipType,
        related_name='orgs',
        blank=True
    )

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('organization_detail', args=(str(self.slug),))

    def membership_directory(self):
        return self.memberships.filter(
            is_listed=True,
            user__is_active=True
        ).order_by('user__last_name')

    def clean(self):
        if self.max_youth_audience_age < self.min_youth_audience_age:
            raise ValidationError("Minimum youth audience age may not "
                                  "be greater than maximum youth audience "
                                  "age.")

    class Meta:
        ordering = ['name']

class ExpertiseManager(models.Manager):
    def of_vouched_users(self):
        return self.filter(
            user__is_active=True,
            user__membership__organization__isnull=False,
            user__membership__is_listed=True
        )

class Expertise(models.Model):
    '''
    Represents an expertise that a user has.
    '''

    CATEGORY_CHOICES = (
        ('youth', 'Youth'),
        ('partnerships', 'Collaboration and Partnerships'),
        ('rfp', 'RFP'),
        ('leveragingresources', 'Leveraging Resources'),
        ('volunteers', 'Mentors and Volunteers'),
        ('sharingoutcomes', 'Sharing Outcomes'),
        ('events', 'Activities and Events'),
        ('programdesign', 'Program Design and Facilitation'),
        ('badges', 'Badges'),
        ('innovation', 'Innovation Design Strategies'),
        ('leveraginghive', 'Leveraging Hive'),
        ('curriculum', 'Curriculum Development'),
        ('assessment', 'Assessment and Evaluative Approaches'),
        ('technology', 'Technological Solutions and Possibilities'),
        ('other', 'Other'),
    )

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    category = models.CharField(
        help_text="The type of the expertise",
        choices=CATEGORY_CHOICES,
        max_length=25,
    )

    details = models.CharField(
        max_length=255,
        blank=True,
        help_text="Details about the expertise",
    )

    user = models.ForeignKey(
        User,
        related_name='skills'
    )

    objects = ExpertiseManager()

class ContentChannelManager(models.Manager):
    use_for_related_fields = True

    def unique_with_icons(self):
        categories = []
        channels = self.all().exclude(category='other')
        for channel in channels.order_by('modified'):
            if channel.category in categories: continue
            categories.append(channel.category)
            yield channel

class ContentChannel(models.Model):
    '''
    Represents a content channel for a Hive organization.
    '''

    FA_ICONS = {
        'facebook': 'fa-facebook-square',
        'youtube': 'fa-youtube-square',
        'vimeo': 'fa-vimeo-square',
        'flickr': 'fa-flickr',
        'tumblr': 'fa-tumblr-square',
        'pinterest': 'fa-pinterest-square',
        'github': 'fa-github-square',
        'instagram': 'fa-instagram',
    }

    CATEGORY_CHOICES = (
        ('facebook', 'Facebook'),
        ('youtube', 'YouTube'),
        ('vimeo', 'Vimeo'),
        ('flickr', 'Flickr'),
        ('tumblr', 'Tumblr'),
        ('pinterest', 'Pinterest'),
        ('github', 'GitHub'),
        ('instagram', 'Instagram'),
        ('other', 'Other'),
    )

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    category = models.CharField(
        help_text="The type of the content channel",
        choices=CATEGORY_CHOICES,
        max_length=15,
    )

    name = models.CharField(
        help_text="The name of the content channel.",
        max_length=100,
        blank=True
    )

    url = models.URLField(
        help_text="The URL of the content channel.",
    )

    organization = models.ForeignKey(
        Organization,
        related_name='content_channels'
    )

    @property
    def fa_icon(self):
        '''
        The Font Awesome icon name for the channel.
        '''

        return self.FA_ICONS.get(self.category, '')

    @property
    def display_name(self):
        '''
        The full name of the content channel, for display to users.
        '''

        for name, display_name in self.CATEGORY_CHOICES:
            if name == self.category:
                break

        if self.category == 'other' and self.name:
            return self.name

        return display_name

    objects = ContentChannelManager()

class MembershipRole(models.Model):
    '''
    Represents a role for a person in the Hive organization, e.g.
    "funding liason", "activity representative", etc.
    '''

    name = models.CharField(
        help_text="The name of the role.",
        max_length=50
    )
    description = models.TextField(
        help_text="Description of the role."
    )
    city = models.ForeignKey(
        City,
        help_text="The Hive city that the role pertains to."
    )

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Membership(models.Model):
    '''
    Represents a person who is a member of an organization.
    '''

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    user = models.OneToOneField(User)
    organization = models.ForeignKey(Organization, blank=True, null=True,
                                     related_name='memberships')
    roles = models.ManyToManyField(MembershipRole, blank=True)
    title = models.CharField(
        help_text="The person's title at their organization.",
        max_length=100,
        blank=True
    )
    bio = models.TextField(
        help_text="The person's biography. Markdown "
                  "and basic HTML tags are allowed.",
        blank=True,
    )
    twitter_name = TwitterNameField(
        help_text="The twitter account for the person.",
        blank=True,
    )
    phone_number = PhoneNumberField(
        help_text="The person's phone number.",
        blank=True
    )
    receives_minigroup_digest = models.BooleanField(
        default=False,
        help_text="Whether the person is sent a daily digest of Minigroup "
                  "activity."
    )
    is_listed = models.BooleanField(
        default=True,
        help_text="Whether the person is listed under their organization in "
                  "the Hive directory."
    )

    @property
    def city(self):
        if self.organization is None: return None
        return self.organization.city

    def get_absolute_url(self):
        return reverse('user_detail', args=(str(self.user.username),))

    def __unicode__(self):
        return u'Membership for %s' % self.user.username

class ImportedUserInfo(models.Model):
    '''
    Represents book-keeping about users who were imported from another
    data source, e.g. a Google Spreadsheet.
    '''

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    user = models.OneToOneField(User)
    was_sent_email = models.BooleanField(
        default=False,
        help_text="Whether the imported user has been sent an email "
                  "informing them of their new account."
    )

    def __unicode__(self):
        return u'Imported user info for %s' % self.user.username

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
    if not (user.email and '@' in user.email): return
    if user.membership.organization: return
    domain_name = user.email.split('@')[1]
    orgs = Organization.objects.filter(email_domain=domain_name)
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
