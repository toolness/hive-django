import urlparse
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.forms import PasswordResetForm
from django.conf import settings

from directory.models import ImportedUserInfo

CONSOLE_EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

def send_email(email, info, dry_run=False):
    use_https = urlparse.urlparse(settings.ORIGIN).scheme == 'https'
    form = PasswordResetForm({'email': email})
    if not form.is_valid(): raise AssertionError('Form is not valid')
    if dry_run:
        original_backend = settings.EMAIL_BACKEND
        settings.EMAIL_BACKEND = CONSOLE_EMAIL_BACKEND
    try:
        form.save(
            use_https=use_https,
            subject_template_name='directory/importeduser_subject.txt',
            email_template_name='directory/importeduser_email.html'
        )
        if not dry_run:
            info.was_sent_email = True
            info.save()
    finally:
        if dry_run:
            settings.EMAIL_BACKEND = original_backend

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--dry-run',
            dest='dry_run',
            default=False,
            help='don\'t actually send emails',
            action='store_true'
        ),
        make_option('--force',
            dest='force',
            default=False,
            help='send emails even to those who were already emailed',
            action='store_true'
        )
    )

    help = '''\
    Email imported users about their new account, excluding 
    users who have already been emailed.

    If no arguments are passed, everyone who hasn't yet been emailed will
    be sent an email. Otherwise, only the users with the given email
    addresses will be contacted.
    '''

    args = '[email1] [email2] ...'

    def handle(self, *args, **kwargs):
        criteria = {}
        if not kwargs['force']: criteria['was_sent_email'] = False
        non_emailed_userinfo = ImportedUserInfo.objects.filter(**criteria)
        if args:
            non_emailed_userinfo = [
                info for info in non_emailed_userinfo
                if info.user.email in args
            ]
        write = self.stdout.write
        if len(non_emailed_userinfo) == 0:
            write('No users need to be emailed.')
            return
        for info in non_emailed_userinfo:
            user = info.user
            write("  Emailing %s <%s>" % (user.get_full_name(), user.email))
            send_email(user.email, info, kwargs['dry_run'])
