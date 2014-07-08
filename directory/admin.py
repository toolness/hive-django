from django.forms import ModelForm
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.auth.admin import UserAdmin
from django.contrib.sites.admin import SiteAdmin

from . import models
from .management.commands.emailimportedusers import send_email

def can_edit_multiple_cities(request):
    '''
    Returns whether the user of the given request can edit multiple
    cities. If not, they are restricted to editing information relevant
    only to the city their organization is part of.
    '''

    return request.user.has_perm('directory.change_city')

class ContentChannelInline(admin.TabularInline):
    model = models.ContentChannel

class OrganizationForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(OrganizationForm, self).__init__(*args, **kwargs)
        if 'membership_type' in self.fields:
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

    def has_change_permission(self, request, obj=None):
        if obj is None:
            return True
        if can_edit_multiple_cities(request):
            return True
        membership = request.user.membership
        if not membership.organization:
            return False
        return membership.organization.city == obj.city

    def get_queryset(self, request):
        qs = super(OrganizationAdmin, self).get_queryset(request)
        if can_edit_multiple_cities(request):
            return qs
        return qs.filter(city=request.user.membership.organization.city)

    def get_form(self, request, obj=None, **kwargs):
        self.readonly_fields = []
        self.exclude = []
        if obj is None:
            self.exclude.extend(['membership_type', 'is_active'])
        if not can_edit_multiple_cities(request):
            if obj is None:
                self.exclude.append('city')
            else:
                self.readonly_fields.append('city')
        return super(OrganizationAdmin, self).get_form(request, obj,
                                                       **kwargs)

    def save_model(request, obj, form, change):
        if not can_edit_multiple_cities(request):
            obj.city = request.user.membership.organization.city
        obj.save()

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
    change_form_template = 'directory/admin_site_change_form.html'
    list_display = SiteAdmin.list_display + ('city',)

admin.site.unregister(Site)
admin.site.register(Site, CitySiteAdmin)
