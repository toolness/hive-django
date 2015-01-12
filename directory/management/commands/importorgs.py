import sys
import csv
import datetime
from optparse import make_option
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.text import slugify

from directory.models import Organization, ContentChannel, \
                             ImportedUserInfo, City
from directory.phonenumber import is_phone_number

MONTHS = ['january', 'february', 'march', 'april', 'may', 'june',
          'july', 'august', 'september', 'october', 'november', 'december']

CONTACT_FIELDS = ['contact-1', 'contact-2', 'contact-3',
                  'other-contacts']
CONTENT_CHANNEL_FIELDS = ['facebook', 'blog', 'youtube',
                          'flickr', 'other-social-content-channels']
NON_ORG_DOMAINS = ['gmail.com']

class DryRunFinished(Exception):
    pass

def split_urls(s):
    '''
    >>> split_urls('meh.com/u\\nu.com/blah')
    ['http://meh.com/u', 'http://u.com/blah']

    >>> split_urls('meh.com/u; u.com/blah')
    ['http://meh.com/u', 'http://u.com/blah']
    '''

    urls = []
    for line in s.splitlines():
        line = line.strip()
        if not line: continue
        if ';' in line:
            lineparts = line.split(';')
        else:
            lineparts = [line]
        for linepart in lineparts:
            linepart = linepart.strip()
            if not linepart: continue
            urls.append(normalize_url(linepart))
    return urls

def parse_content_channels(s):
    '''
    >>> parse_content_channels('http://facebook.com/blah')
    [('facebook', 'http://facebook.com/blah')]

    >>> parse_content_channels('http://twitter.com/blah')
    []

    >>> parse_content_channels('\\n\\n\\nmeh.com/blah\\n\\n\\n')
    [('other', 'http://meh.com/blah')]
    '''

    channels = []
    for url in split_urls(s):
        url = url.strip()
        if not url: continue
        if 'twitter.com' in url: continue
        url = normalize_url(url)
        url_category = 'other'
        for category, name in ContentChannel.CATEGORY_CHOICES:
            if ('%s.com' % category) in url.lower():
                url_category = category
        channels.append((url_category, url))
    return channels

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
    result['full_name'] = lines[0]
    result['first_name'], result['last_name'] = lines[0].split(' ', 1)
    result['title'] = lines[1]
    for line in lines[2:]:
        line = line.strip()
        if '@' in line and not line.startswith('@'):
            result['email'] = line
        elif line.startswith('@'):
            result['twitter'] = line[1:]
        elif is_phone_number(line):
            result['phone'] = line
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
        make_option('--city',
            dest='city',
            help='city slug to import orgs under',
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
        total_twitterers = 0
        total_phone_numbers = 0
        total_contacts = 0
        orginfos = convert_rows_to_dicts(rows)
        for info in orginfos:
            orgname = unicode(info['name-of-organization'])
            self.log('Importing %s...' % orgname)
            try:
                contacts = []
                email_domain = ''
                for field in CONTACT_FIELDS:
                    contacts.extend(parse_contacts(info[field], self.stderr))

                total_contacts += len(contacts)
                if contacts:
                    email_domain = contacts[0]['email'].split('@')[1]
                    if email_domain in NON_ORG_DOMAINS:
                        email_domain = ''

                if email_domain:
                    self.debug("  Email domain is %s." % email_domain)

                min_age, max_age = parse_age_range(info['youth-audience'])
                org = Organization(
                    city=self.city,
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

                channels = []
                for field in CONTENT_CHANNEL_FIELDS:
                    channels.extend(parse_content_channels(info[field]))

                for category, url in channels:
                    self.debug("  Importing channel: %s (%s)" % (
                        url,
                        category
                    ))
                    channel = ContentChannel(
                        category=category,
                        url=url,
                        organization=org
                    )
                    channel.full_clean()
                    channel.save()

                for contact in contacts:
                    username = unicode(contact['full_name'])
                    username = slugify(username)
                    username = username.replace('-', '')

                    self.debug("  Importing contact: %s (%s, %s, %s)." % (
                        contact['full_name'],
                        username,
                        contact['title'],
                        contact['email']
                    ))

                    user = User(
                        username=username,
                        first_name=contact['first_name'],
                        last_name=contact['last_name'],
                        is_active=True,
                        email=contact['email'],
                    )
                    user.set_password(User.objects.make_random_password())
                    user.full_clean()
                    user.save()
                    membership = user.membership
                    membership.organization = org
                    membership.title = contact['title']
                    if ('twitter' in contact and
                        contact['twitter'] != org.twitter_name):
                        membership.twitter_name = contact['twitter']
                        total_twitterers += 1
                    if 'phone' in contact:
                        membership.phone_number = contact['phone']
                        total_phone_numbers += 1
                    membership.full_clean()
                    membership.save()
                    import_info = ImportedUserInfo(user=user)
                    import_info.save()
            except Exception:
                self.stderr.write('Error importing row '
                                  '%d (%s)' % (info['row'], orgname))
                raise
        self.debug('Total orgs: %d' % len(orginfos))
        self.debug('Total contacts: %d' % total_contacts)
        self.debug('Total twitterers: %d' % total_twitterers)
        self.debug('Total phone numbers: %d' % total_phone_numbers)

    def set_city(self, city_slug):
        if not city_slug:
            raise CommandError('City not provided (use --city option).')
        cities = City.objects.filter(slug=city_slug)
        if not cities:
            raise CommandError('City with slug "%s" not found.' % city_slug)
        self.city = cities[0]

    def handle(self, *args, **options):
        self.verbosity = int(options['verbosity'])
        self.latest_row = None
        self.set_city(options['city'])
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

    def unicode_row(self, row):
        return [item.decode('utf-8') for item in row]

    def get_rows(self, *args, **options):
        fileinput = options.get('fileinput')
        if len(args) != 1 and not fileinput:
            raise CommandError('Please specify a CSV filename.')
        reader = csv.reader(fileinput or open(args[0], 'rb'))
        return [self.unicode_row(row) for row in reader]
