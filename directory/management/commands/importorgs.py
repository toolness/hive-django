import csv
import datetime
from optparse import make_option
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.text import slugify

from directory.models import Organization

class DryRunFinished(Exception):
    pass

def parse_twitter_name(t):
    if not t: return ''
    if t[0] != '@': raise Exception('not a twitter name: %s' % t)
    return t[1:]

def normalize_url(url):
    if url.startswith('http://') or url.startswith('https://'):
        return url
    return 'http://%s' % url

def convert_rows_to_dicts(rows):
    column_names = None
    dicts = []
    for i, row in enumerate(rows):
        if i == 0:
            # Column headers.
            column_names = tuple([slugify(unicode(val)) for val in row])
        elif i == 1:
            # Column notes/instructions.
            pass
        else:
            # An actual row with information about an org.
            info = {'row': i + 1}
            for colnum, val in enumerate(row):
                colname = column_names[colnum]
                if colname:
                    info[colname] = val
            dicts.append(info)
    return dicts

class ImportOrgsCommand(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--dry-run',
            dest='dry_run',
            default=False,
            help='don\'t commit imported data to database',
            action='store_true'
        ),
    )

    def get_rows(self, *args, **options):
        raise NotImplementedError()

    def log(self, msg):
        self.stdout.write(msg)

    def debug(self, msg):
        if self.verbosity >= 2:
            self.stdout.write(msg)

    def import_rows(self, rows):
        for info in convert_rows_to_dicts(rows):
            orgname = unicode(info['name-of-organization'])
            self.log('Importing %s...' % orgname)
            try:
                org = Organization(
                    name=orgname,
                    slug=slugify(orgname)[:50],
                    hive_member_since=datetime.datetime.now(),
                    mission=info['organizational-mission'],
                    website=normalize_url(info['url']),
                    address=info['mailing-address'],
                    twitter_name=parse_twitter_name(info['twitter']),
                    # TODO: Parse the 'hive-nyc-member-since' column.
                    # TODO: Import youth audience min/max age.
                    # TODO: Import email domain, if any.
                )
                org.full_clean()
                org.save()
                # TODO: Import organization content channels.
                # TODO: Import users from 'contact-1' columns etc.
            except Exception:
                self.stderr.write('Error importing row '
                                  '%d (%s)' % (info['row'], orgname))
                raise

    def handle(self, *args, **options):
        self.verbosity = int(options['verbosity'])
        self.latest_row = None
        rows = self.get_rows(*args, **options)

        try:
            with transaction.atomic():
                self.import_rows(rows)
                if options['dry_run']: raise DryRunFinished()
        except DryRunFinished:
            self.stdout.write("Dry run complete.")

class Command(ImportOrgsCommand):
    help = 'Import organizations and users from a CSV file.'
    args = '<filename>'

    def get_rows(self, *args, **options):
        if len(args) != 1:
            raise CommandError('Please specify a CSV filename.')
        reader = csv.reader(open(args[0], 'rb'))
        return [row for row in reader]
