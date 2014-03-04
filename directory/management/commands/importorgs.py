import csv
from optparse import make_option
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from directory.models import Organization

class DryRunFinished(Exception):
    pass

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

def import_rows(rows):
    orgs = convert_rows_to_dicts(rows)
    print orgs
    raise NotImplementedError("TODO: Import stuff here!")

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

    def handle(self, *args, **options):
        rows = self.get_rows(*args, **options)

        try:
            with transaction.atomic():
                import_rows(rows)
                if options['dry_run']: raise DryRunFinished()
        except DryRunFinished:
            print "Dry run complete."

class Command(ImportOrgsCommand):
    help = 'Import organizations and users from a CSV file.'
    args = '<filename>'

    def get_rows(self, *args, **options):
        if len(args) != 1:
            raise CommandError('Please specify a CSV filename.')
        reader = csv.reader(open(args[0], 'rb'))
        return [row for row in reader]
