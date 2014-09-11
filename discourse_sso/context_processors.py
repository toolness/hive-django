from django.conf import settings

def discourse_sso_origin(request=None):
    return {'DISCOURSE_SSO_ORIGIN': settings.DISCOURSE_SSO_ORIGIN}
