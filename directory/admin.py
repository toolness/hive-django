from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from . import models

class OrganizationAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}

admin.site.register(models.Organization, OrganizationAdmin)

class MembershipInline(admin.StackedInline):
    verbose_name_plural = 'Organizational Membership'
    model = models.Membership
    can_delete = False

class MembershipUserAdmin(UserAdmin):
    inlines = (MembershipInline,)

admin.site.unregister(User)
admin.site.register(User, MembershipUserAdmin)
