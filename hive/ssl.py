import urlparse
from django.http import HttpResponsePermanentRedirect
from django.core.exceptions import MiddlewareNotUsed

from django.conf import settings

class SslMiddleware(object):
    def __init__(self):
        if urlparse.urlparse(settings.ORIGIN).scheme != 'https':
            raise MiddlewareNotUsed()

class RedirectToHttpsMiddleware(SslMiddleware):
    def process_request(self, request):
        if not request.is_secure():
            return HttpResponsePermanentRedirect(settings.ORIGIN +
                                                 request.path)

class HstsMiddleware(SslMiddleware):
    def process_response(self, request, response):
        response["Strict-Transport-Security"] = "max-age=31536000; " \
                                                "includeSubdomains"
        return response
