from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from . import models

class ContentChannelInline(admin.TabularInline):
    model = models.ContentChannel

class OrganizationAdmin(admin.ModelAdmin):
    inlines = (ContentChannelInline,)
    prepopulated_fields = {"slug": ("name",)}

admin.site.register(models.Organization, OrganizationAdmin)

class MembershipInline(admin.StackedInline):
    verbose_name_plural = 'Organizational Membership'
    model = models.Membership
    can_delete = False

class MembershipUserAdmin(UserAdmin):
    inlines = (MembershipInline,)

    def get_formsets(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            if isinstance(inline, MembershipInline) and obj is None:
                continue
            yield inline.get_formset(request, obj)

admin.site.unregister(User)
admin.site.register(User, MembershipUserAdmin)
