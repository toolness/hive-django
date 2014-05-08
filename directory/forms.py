from django.conf import settings
from django.forms import ModelForm
from django.forms.models import inlineformset_factory
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper

from .models import Organization, Membership, \
                    ContentChannel, Expertise

ExpertiseFormSet = inlineformset_factory(
    User, Expertise,
    fields = ['category', 'details'],
    help_texts = {'category': '', 'details': ''},
    labels = {'category': 'Category', 'details': 'Additional notes'}
)

class ExpertiseFormSetHelper(FormHelper):
    form_tag = False
    template = 'directory/table_inline_formset.html'

ContentChannelFormSet = inlineformset_factory(
    Organization, ContentChannel,
    fields = ['category', 'name', 'url'],
    help_texts = {'category': '', 'name': '', 'url': ''},
    labels = {'url': 'URL', 'name': 'Name (if other)'}
)

class ChannelFormSetHelper(FormHelper):
    form_tag = False
    template = 'directory/table_inline_formset.html'

class MembershipForm(ModelForm):
    class Meta:
        model = Membership
        fields = ['title', 'bio', 'twitter_name', 'phone_number',
                  'is_listed']
        if 'minigroup_digestif' in settings.INSTALLED_APPS:
            fields.append('receives_minigroup_digest')
        labels = {
            'receives_minigroup_digest': 'Send me a daily digest of all '
                                         'activity on the Hive minigroup.',
            'is_listed': 'List me under my organization\'s entry in the '
                         'Hive member directory.'
        }
        help_texts = {
            'is_listed': '',
            'receives_minigroup_digest': '',
            'bio': 'Your mini-biography. Markdown and basic HTML tags '
                   'are allowed.',
            'twitter_name': 'Your twitter name, e.g. "leahatplay".',
            'phone_number': 'Your phone number, e.g. 123-456-7890.',
            'title': 'Your title at your organization, e.g. '
                     '"Executive Director of Awesome".',
        }

class UserProfileForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']

class OrganizationForm(ModelForm):
    class Meta:
        model = Organization
        fields = ['name', 'website', 'address', 'twitter_name',
                  'mission']
