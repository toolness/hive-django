from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

CITY_EDITOR_PERMS = (
    'add_organization',
    'change_organization',
    'add_user',
    'change_user',
    'change_membership',
    'add_membershiprole',
    'change_membershiprole',
    'delete_membershiprole',
    'add_organizationmembershiptype',
    'change_organizationmembershiptype',
    'delete_organizationmembershiptype',
    'change_flatpage',
)

MULTI_CITY_EDITOR_PERMS = CITY_EDITOR_PERMS + (
    'add_city',
    'change_city',
    'add_cityblog',
    'change_cityblog',
    'delete_cityblog',
)

class Command(BaseCommand):
    help = '''\
    Initializes some helpful initial permission groups.
    '''

    def set_perms(self, groupname, codenames):
        self.stdout.write("Setting permissions for group '%s'." % groupname)
        try:
            group = Group.objects.get(name=groupname)
        except Group.DoesNotExist:
            group = Group(name=groupname)
            group.save()
        group.permissions = [
            Permission.objects.get(codename=codename)
            for codename in codenames
        ]
        group.save()

    def handle(self, *args, **kwargs):
        self.set_perms('City Editors', CITY_EDITOR_PERMS)
        self.set_perms('Multi-City Editors', MULTI_CITY_EDITOR_PERMS)
        self.stdout.write("Done.")
        self.stdout.write("Please do not manually change these "
                          "groups; they may be updated in the future.")
