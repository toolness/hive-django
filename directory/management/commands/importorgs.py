import sys
import csv
import datetime
from optparse import make_option
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.text import slugify

from directory.models import Organization

MONTHS = ['january', 'february', 'march', 'april', 'may', 'june',
          'july', 'august', 'september', 'october', 'november', 'december']

CONTACT_FIELDS = ['contact-1', 'contact-2', 'contact-3',
                  'other-contacts']

NON_ORG_DOMAINS = ['gmail.com']

class DryRunFinished(Exception):
    pass

def parse_contacts(s, stderr=sys.stderr):
    s = s.strip()
    if not s: return []
    results = [parse_contact(chunk, stderr) for chunk in s.split('\n\n')]
    return [result for result in results if result is not None]

def parse_contact(s, stderr=sys.stderr):
    result = {}
    lines = s.splitlines()
    if len(lines) < 3:
        stderr.write('WARNING: cannot parse contact: %s' % repr(s))
        return None
    result['first_name'], result['last_name'] = lines[0].split(' ', 1)
    result['title'] = lines[1]
    for line in lines[2:]:
        if '@' in line and not line.startswith('@'):
            result['email'] = line
    if 'email' not in result:
        stderr.write('WARNING: no email address for %s %s' % (
            result['first_name'], result['last_name']
        ))
        return None
    return result

def parse_age_range(s):
    '''
    >>> parse_age_range('11 - 18, 19 - 100')
    (11, 18)
    '''

    s = s.strip()
    if not s: return (0, 100)
    s = s.split(',')[0].strip()
    min_age, max_age = s.split(' - ')
    return int(min_age), int(max_age)

def parse_month_and_year(s):
    '''
    >>> parse_month_and_year('January 2011')
    datetime.date(2011, 1, 1)
    '''

    s = s.strip()
    if not s: return datetime.date.today()
    month, year = s.split()
    return datetime.date(int(year), int(MONTHS.index(month.lower())) + 1, 1)

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
                contacts = []
                email_domain = ''
                for field in CONTACT_FIELDS:
                    contacts.extend(parse_contacts(info[field], self.stderr))

                for contact in contacts:
                    self.debug("  Found contact: %s %s (%s, %s)." % (
                        contact['first_name'],
                        contact['last_name'],
                        contact['title'],
                        contact['email']
                    ))

                if contacts:
                    email_domain = contacts[0]['email'].split('@')[1]
                    if email_domain in NON_ORG_DOMAINS:
                        email_domain = ''

                if email_domain:
                    self.debug("  Email domain is %s." % email_domain)

                min_age, max_age = parse_age_range(info['youth-audience'])
                org = Organization(
                    name=orgname,
                    slug=slugify(orgname)[:50],
                    hive_member_since=parse_month_and_year(
                        info['hive-nyc-member-since']
                    ),
                    mission=info['organizational-mission'],
                    website=normalize_url(info['url']),
                    address=info['mailing-address'],
                    twitter_name=parse_twitter_name(info['twitter']),
                    min_youth_audience_age=min_age,
                    max_youth_audience_age=max_age,
                    email_domain=email_domain
                )
                org.full_clean()
                org.save()
                # TODO: Import organization content channels.
                # TODO: Actually import contacts.
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
