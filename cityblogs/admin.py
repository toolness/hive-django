from django.contrib import admin

from directory.admin import CityScopedAdmin, can_edit_multiple_cities
from .models import CityBlog

class OneToOneCityScopedAdmin(CityScopedAdmin):
    def has_add_permission(self, request):
        super_self = super(OneToOneCityScopedAdmin, self)
        if not super_self.has_add_permission(request):
            return False
        if can_edit_multiple_cities(request):
            return True
        city = request.user.membership.city
        if city is None:
            return False
        if self.model.objects.filter(city=city):
            return False
        return True

class CityBlogAdmin(OneToOneCityScopedAdmin):
    pass

admin.site.register(CityBlog, CityBlogAdmin)
