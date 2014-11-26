from django.contrib import admin

from directory.admin import CityAdmin
from directory.models import City
from .models import CityBlog

class CityBlogInline(admin.TabularInline):
    model = CityBlog

class CityBlogAdmin(CityAdmin):
    inlines = CityAdmin.inlines + [CityBlogInline]

admin.site.unregister(City)
admin.site.register(City, CityBlogAdmin)
