from optparse import make_option
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.core.management import call_command

from directory.models import Organization

def create_user(username, password=None, organization=None, **kwargs):
    user = User(username=username, **kwargs)
    if password:
        user.set_password(password)
    user.save()
    if organization:
        if isinstance(organization, basestring):
            organization = Organization.objects.get(slug=organization)
        user.membership.organization = organization
        user.membership.save()
    return user

class Command(BaseCommand):
    help = 'Seeds the database with sample organizations and users.'
    option_list = BaseCommand.option_list + (
        make_option('--password',
            dest='password',
            default='test',
            help='Specify password to use for all seeded users'
        ),
    )

    def handle(self, *args, **options):
        passwd = options['password']

        call_command('loaddata', 'wnyc.json', 'hivenyc.json', 'amnh.json')
        create_user('admin', password=passwd, email='admin@example.org',
                    is_staff=True, is_superuser=True)

        john = create_user('john', password=passwd, organization='wnyc',
                           first_name='John', last_name='Doe',
                           email='johndoe@wnyc.org')
        john.membership.title = 'Intern'
        john.membership.is_listed = False
        john.membership.save()

        jane = create_user('jane', password=passwd, organization='amnh',
                           first_name='Jane', last_name='Doe',
                           email='janedoe@amnh.org')
        jane.membership.title = 'Executive Director'
        jane.membership.save()

        create_user('inactive', password=passwd, organization='wnyc',
                    first_name='Inactive', last_name='User',
                    is_active=False)

        hivenyc = Organization.objects.get(slug='hivenyc')
        hivenyc.is_active = False
        hivenyc.name = "%s **INACTIVE**" % hivenyc.name
        hivenyc.save()

        site = Site.objects.get(pk=1)
        site.domain = settings.ALLOWED_HOSTS[0]
        site.name = "Hive TESTING"
        site.save()

        print "Database seeded. Login as admin with password '%s' " \
              "to view the site as an administrator. All seeded users " \
              "have the same password." % passwd
