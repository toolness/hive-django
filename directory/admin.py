from django.forms import ModelForm
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.flatpages.models import FlatPage
from django.contrib.auth.admin import UserAdmin
from django.contrib.sites.admin import SiteAdmin
from django.contrib.flatpages.admin import FlatPageAdmin
from django.db.models import Q
from django.utils.translation import ugettext, ugettext_lazy as _

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

class CityScopedAdmin(admin.ModelAdmin):
    '''
    For models with a 'city' field, this admin ensures that City Editors
    only have the ability to edit models related to their city.
    '''

    # Additional fields to exclude from the 'add' form.
    exclude_from_add = []

    def has_change_permission(self, request, obj=None):
        if obj is None:
            return True
        if can_edit_multiple_cities(request):
            return True
        return request.user.membership.city == obj.city

    has_delete_permission = has_change_permission

    def get_queryset(self, request):
        qs = super(CityScopedAdmin, self).get_queryset(request)
        if can_edit_multiple_cities(request):
            return qs
        return qs.filter(city=request.user.membership.city)

    def get_form(self, request, obj=None, **kwargs):
        self.readonly_fields = []
        self.exclude = []
        if obj is None:
            self.exclude.extend(self.exclude_from_add)
        if not can_edit_multiple_cities(request):
            if obj is None:
                self.exclude.append('city')
            else:
                self.readonly_fields.append('city')
        return super(CityScopedAdmin, self).get_form(request, obj,
                                                     **kwargs)

    def save_model(self, request, obj, form, change):
        if not can_edit_multiple_cities(request):
            obj.city = request.user.membership.city
        obj.save()

class OrganizationAdmin(CityScopedAdmin):
    form = OrganizationForm
    inlines = (ContentChannelInline,)
    list_display = ('name', 'city')
    list_filter = ('city',)
    prepopulated_fields = {"slug": ("name",)}

    exclude_from_add = ['membership_type', 'is_active']

admin.site.register(models.Organization, OrganizationAdmin)

class CityAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}

admin.site.register(models.City, CityAdmin)

class OrganizationMembershipTypeAdmin(CityScopedAdmin):
    list_display = ('name', 'city')
    list_filter = ('city',)

admin.site.register(models.OrganizationMembershipType,
                    OrganizationMembershipTypeAdmin)

class MembershipRoleAdmin(CityScopedAdmin):
    list_display = ('name', 'city')
    list_filter = ('city',)

admin.site.register(models.MembershipRole, MembershipRoleAdmin)

class MembershipForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(MembershipForm, self).__init__(*args, **kwargs)
        self.fields['roles'].queryset = models.MembershipRole.objects.filter(
            city=self.instance.city
        )

class MembershipInline(admin.StackedInline):
    form = MembershipForm
    verbose_name_plural = 'Organizational Membership'
    model = models.Membership
    can_delete = False

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if (not can_edit_multiple_cities(request) and
            db_field.name == 'organization'):
            kwargs['queryset'] = models.Organization.objects.filter(
                city=request.user.membership.city
            )
        return super(MembershipInline, self).formfield_for_foreignkey(
            db_field, request, **kwargs
        )

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
    editor_fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active',)}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

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

    def get_queryset(self, request):
        qs = super(MembershipUserAdmin, self).get_queryset(request)
        if can_edit_multiple_cities(request):
            return qs
        return qs.filter(
            Q(membership__organization=None) |
            Q(membership__organization__city=request.user.membership.city)
        )

    def has_change_permission(self, request, obj=None):
        if obj is None:
            return True
        if can_edit_multiple_cities(request):
            return True
        if not obj.membership.city:
            return True
        return request.user.membership.city == obj.membership.city

    def get_fieldsets(self, request, obj=None):
        if obj is not None and not request.user.is_superuser:
            return self.editor_fieldsets
        return super(MembershipUserAdmin, self).get_fieldsets(request, obj)

admin.site.unregister(User)
admin.site.register(User, MembershipUserAdmin)

class CitySiteAdmin(SiteAdmin):
    change_form_template = 'directory/admin_site_change_form.html'
    list_display = SiteAdmin.list_display + ('city',)

admin.site.unregister(Site)
admin.site.register(Site, CitySiteAdmin)

class CityScopedFlatPageAdmin(FlatPageAdmin):
    city_editor_fieldsets = (
        (None, {'fields': ('url', 'title', 'content')}),
    )

    def get_fieldsets(self, request, obj=None):
        if obj is not None and not can_edit_multiple_cities(request):
            return self.city_editor_fieldsets
        return super(self.__class__, self).get_fieldsets(request, obj)

    def has_change_permission(self, request, obj=None):
        if obj is None:
            return True
        return obj in self.get_queryset(request)

    def get_queryset(self, request):
        qs = super(CityScopedFlatPageAdmin, self).get_queryset(request)
        if can_edit_multiple_cities(request):
            return qs
        return qs.filter(sites__city=request.user.membership.city)

admin.site.unregister(FlatPage)
admin.site.register(FlatPage, CityScopedFlatPageAdmin)
