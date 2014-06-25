from django.conf import settings

def multi_city(request=None):
    return {'MULTI_CITY': settings.MULTI_CITY}
