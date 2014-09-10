from django.conf import settings
from django import forms
from django.forms.models import inlineformset_factory
from django.contrib.auth.models import User
from django.template import loader
from crispy_forms.helper import FormHelper

from .models import Organization, Membership, City, \
                    ContentChannel, Expertise

ExpertiseFormSet = inlineformset_factory(
    User, Expertise,
    fields = ['category', 'details'],
    help_texts = {'category': '', 'details': ''},
    labels = {'category': 'Category', 'details': 'Additional notes'},
    extra = 1
)

class ExpertiseFormSetHelper(FormHelper):
    form_tag = False
    template = 'directory/table_inline_formset.html'

ContentChannelFormSet = inlineformset_factory(
    Organization, ContentChannel,
    fields = ['category', 'name', 'url'],
    help_texts = {'category': '', 'name': '', 'url': ''},
    labels = {'url': 'URL', 'name': 'Name (if other)'},
    extra = 1
)

class ChannelFormSetHelper(FormHelper):
    form_tag = False
    template = 'directory/table_inline_formset.html'

class MembershipForm(forms.ModelForm):
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

class UserApplicationForm(forms.Form):
    city = forms.ModelChoiceField(
        label='Which Hive city are you part of?',
        queryset=City.objects.all()
    )
    info = forms.CharField(
        label=('Please provide a bit of information on who you are, '
               'and what organization (if any) you belong to. Also '
               'include your phone number in case we need to verify '
               'your identity.'),
        widget=forms.Textarea,
        max_length=500
    )

    def save(self, user,
             from_email=None,
             subject_template_name='directory/user_apply_subject.txt',
             email_template_name='directory/user_apply_email.html'):
        # A lot of this is just taken from Django auth's PasswordResetForm.
        from django.core.mail import send_mail
        city = self.cleaned_data['city']
        c = {
            'ORIGIN': settings.ORIGIN,
            'city': city,
            'user': user,
            'info': self.cleaned_data['info']
        }
        recipients = [staff.email for staff in User.objects.filter(
            membership__organization__city=city,
            is_staff=True
        )]
        if not recipients:
            recipients = [su.email for su in User.objects.filter(
                is_superuser=True
            )]
            c['recipient_is_superuser'] = True
        subject = loader.render_to_string(subject_template_name, c)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        email = loader.render_to_string(email_template_name, c)
        send_mail(subject, email, from_email, recipients)

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']

class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['name', 'website', 'address', 'twitter_name',
                  'mission']
