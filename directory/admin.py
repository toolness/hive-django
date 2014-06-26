from django.forms import ModelForm
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.auth.admin import UserAdmin
from django.contrib.sites.admin import SiteAdmin

from . import models
from .management.commands.emailimportedusers import send_email

class ContentChannelInline(admin.TabularInline):
    model = models.ContentChannel

class OrganizationForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(OrganizationForm, self).__init__(*args, **kwargs)
        qs = models.OrganizationMembershipType.objects.filter(
            city=self.instance.city
        )
        self.fields['membership_type'].queryset = qs

class OrganizationAdmin(admin.ModelAdmin):
    form = OrganizationForm
    inlines = (ContentChannelInline,)
    list_display = ('name', 'city')
    list_filter = ('city',)
    prepopulated_fields = {"slug": ("name",)}

admin.site.register(models.Organization, OrganizationAdmin)

class CityAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}

admin.site.register(models.City, CityAdmin)

class OrganizationMembershipTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'city')
    list_filter = ('city',)

admin.site.register(models.OrganizationMembershipType,
                    OrganizationMembershipTypeAdmin)

class MembershipRoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'city')
    list_filter = ('city',)

admin.site.register(models.MembershipRole, MembershipRoleAdmin)

class MembershipForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(MembershipForm, self).__init__(*args, **kwargs)
        if self.instance.organization is None:
            qs = models.MembershipRole.objects.none()
        else:
            qs = models.MembershipRole.objects.filter(
                city=self.instance.organization.city
            )
        self.fields['roles'].queryset = qs

class MembershipInline(admin.StackedInline):
    form = MembershipForm
    verbose_name_plural = 'Organizational Membership'
    model = models.Membership
    can_delete = False

class ImportedUserInfoInline(admin.StackedInline):
    verbose_name_plural = 'Imported User Information'
    model = models.ImportedUserInfo
    can_delete = False
    readonly_fields = ['was_sent_email']
    fieldsets = (
        ('Book-keeping Information', {
            'fields': ('was_sent_email',),
            'classes': ('collapse',)
        }),
    )

class MembershipUserAdmin(UserAdmin):
    inlines = (ImportedUserInfoInline, MembershipInline,)
    actions = UserAdmin.actions + ['email_imported_users']
    list_filter = UserAdmin.list_filter + ('membership__organization__city',)
    list_display = ('username', 'email', 'first_name', 'last_name',
                    'is_staff', 'organization')

    def organization(self, obj):
        if obj.membership.organization:
            return obj.membership.organization.name
        return ''

    organization.admin_order_field = 'membership__organization__name'

    def email_imported_users(self, request, queryset):
        for user in queryset:
            if not user.email:
                self.message_user(
                    request,
                    "The user '%s' was not invited because they have no "
                    "email address." % user.username
                )
                continue
            info, created = models.ImportedUserInfo.objects.get_or_create(
                user=user
            )
            send_email(user.email, info)
            self.message_user(request,
                              "Sent an invite to '%s'." % user.username)

    email_imported_users.short_description = '''\
    Invite selected users to join the site
    '''

    def get_formsets(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            if (obj is None and
                (isinstance(inline, MembershipInline) or
                 isinstance(inline, ImportedUserInfoInline))):
                continue
            yield inline.get_formset(request, obj)

admin.site.unregister(User)
admin.site.register(User, MembershipUserAdmin)

class CitySiteAdmin(SiteAdmin):
    list_display = SiteAdmin.list_display + ('city',)

admin.site.unregister(Site)
admin.site.register(Site, CitySiteAdmin)
