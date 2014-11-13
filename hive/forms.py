from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import User

class HiveAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="Username or email address",
        max_length=254
    )

    def clean(self):
        username_or_email = self.cleaned_data.get('username')
        if username_or_email and '@' in username_or_email:
            users = User.objects.filter(email=username_or_email)
            if len(users) == 1:
                self.cleaned_data['username'] = users[0].username
        super(HiveAuthenticationForm, self).clean()
