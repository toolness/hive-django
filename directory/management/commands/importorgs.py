from optparse import make_option
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from directory.models import Organization

class DryRunFinished(Exception):
    pass

def import_spreadsheet(sheet):
    i = 1
    for row in sheet.get_all_values():
        # TODO: Finish this.
        print row[2]
        i += 1

class Command(BaseCommand):
    help = 'Import organizations and users from a Google spreadsheet.'
    args = '<username> <password> <spreadsheet-key>'
    option_list = BaseCommand.option_list + (
        make_option('--dry-run',
            dest='dry_run',
            default=False,
            help='don\'t commit imported data to database',
            action='store_true'
        ),
    )

    def handle(self, *args, **options):
        try:
            import gspread
        except ImportError:
            raise CommandError('Please run "pip install gspread".')

        if len(args) != 3:
            raise CommandError('Insufficient arguments.')

        username, password, key = args
        gs = gspread.login(username, password)
        try:
            with transaction.atomic():
                import_spreadsheet(gs.open_by_key(key).sheet1)
                if options['dry_run']: raise DryRunFinished()
        except DryRunFinished:
            print "Dry run complete."
