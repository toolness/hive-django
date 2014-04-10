import urlparse
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.forms import PasswordResetForm
from django.conf import settings

from directory.models import ImportedUserInfo

class Command(BaseCommand):
    help = 'Email imported users about their new account.'

    def handle(self, *args, **kwargs):
        use_https = (urlparse.urlparse(settings.ORIGIN).scheme == 'https')
        non_emailed_userinfo = ImportedUserInfo.objects.filter(
            was_sent_email=False
        )
        write = self.stdout.write
        if len(non_emailed_userinfo) == 0:
            write('No users need to be emailed.')
            return
        for info in non_emailed_userinfo:
            user = info.user
            write("  Emailing %s <%s>" % (user.get_full_name(), user.email))
            form = PasswordResetForm({'email': user.email})
            if not form.is_valid(): raise AssertionError('Form is not valid')
            form.save(
                use_https=use_https,
                subject_template_name='directory/importeduser_subject.txt',
                email_template_name='directory/importeduser_email.html'
            )
            info.was_sent_email = True
            info.save()
