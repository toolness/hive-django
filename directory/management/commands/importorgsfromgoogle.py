from django.core.management.base import CommandError

from .importorgs import ImportOrgsCommand

class Command(ImportOrgsCommand):
    help = 'Import organizations and users from a Google spreadsheet.'
    args = '<username> <password> <spreadsheet-key>'

    def get_rows(self, *args, **options):
        try:
            import gspread
        except ImportError:
            raise CommandError('Please run "pip install gspread".')

        if len(args) != 3:
            raise CommandError('Insufficient arguments.')

        username, password, key = args
        gs = gspread.login(username, password)
        return gs.open_by_key(key).sheet1.get_all_values()
